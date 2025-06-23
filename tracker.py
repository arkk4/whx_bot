# tracker.py
import sqlite3
import os
import logging
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# --- Налаштування ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_PATH = os.environ.get("DATABASE_PATH", "/var/lib/wh_bot/bot_database.db")
BASE_URL = os.environ.get("BASE_URL", "https://www.woninghuren.nl/aanbod/te-huur/details/")

app = FastAPI()

# Додаємо CORS, щоб браузер дозволив POST-запит зі сторінки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def db_execute(query: str, params: tuple = ()):
    """Утиліта для виконання запитів до БД з увімкненим WAL."""
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=25.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(query, params)
            conn.commit()
    except Exception as e:
        logging.error(f"Помилка виконання запиту до БД: {e}")

@app.get("/track")
def track_click(user_id: int, url_key: str, request: Request):
    user_agent = request.headers.get('user-agent')
    db_execute(
        'INSERT INTO url_clicks (user_id, url_key, user_agent) VALUES (?, ?, ?)',
        (user_id, url_key, user_agent)
    )
    final_url = BASE_URL + url_key
    logging.info(f"Перенаправлення користувача {user_id} на {final_url}")
    return RedirectResponse(url=final_url)

@app.get("/get_tz", response_class=HTMLResponse)
def get_timezone_page(user_id: int):
    # Ця HTML-сторінка буде показана користувачу в Telegram
    html_content = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name-viewport" content="width=device-width, initial-scale=1.0">
        <title>Налаштування часового поясу</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f2f5; text-align: center; }}
            .container {{ padding: 20px; background-color: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            #status {{ margin-top: 15px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Визначення часового поясу</h2>
            <p>Зачекайте, ми автоматично визначаємо ваш часовий пояс...</p>
            <p id="status">🤔 Визначаю...</p>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', (event) => {{
                const statusEl = document.getElementById('status');
                try {{
                    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                    statusEl.textContent = `✅ Ваш часовий пояс: ${{userTimezone}}`;
                    
                    fetch('/set_tz', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                        body: `user_id={user_id}&timezone=${{encodeURIComponent(userTimezone)}}`
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if(data.status === 'ok') {{
                            statusEl.innerHTML += '<br>✔️ Збережено! Можете закрити це вікно.';
                        }} else {{
                            statusEl.innerHTML += '<br>❌ Помилка збереження.';
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error:', error);
                        statusEl.innerHTML += '<br>❌ Не вдалося зв\\'язатися з сервером.';
                    }});

                }} catch (e) {{
                    statusEl.textContent = '❌ Не вдалося визначити ваш часовий пояс.';
                    console.error(e);
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/set_tz")
def set_timezone(user_id: int = Form(...), timezone: str = Form(...)):
    if not user_id or not timezone:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Missing user_id or timezone"})

    logging.info(f"Встановлення часового поясу '{timezone}' для користувача {user_id}")
    db_execute(
        "UPDATE users SET timezone = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
        (timezone, user_id)
    )
    return JSONResponse(content={"status": "ok"})

@app.get("/health")
def health_check():
    return {"status": "ok"}