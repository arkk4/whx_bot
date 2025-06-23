# main.py
import requests
import time
import os
import logging
import colorlog
from colorlog import ColoredFormatter
import sys
import sqlite3
import re
import asyncio
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple


import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, LabeledPrice, Message, CallbackQuery
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes,
    MessageHandler, filters, PreCheckoutQueryHandler
)

# Імпортуємо локалізацію з окремого файлу
from i18n import TRANSLATIONS



# --- Конфігурація ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
PROVIDER_TOKEN = os.environ.get("PROVIDER_TOKEN", "")
TRACKER_BASE_URL = os.environ.get("TRACKER_BASE_URL", "")

LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "/var/log/whx.log")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "")
API_URL = os.environ.get("API_URL", "")
BASE_URL = os.environ.get("BASE_URL", "")
IMAGE_BASE_URL = os.environ.get("IMAGE_BASE_URL", "")

TRACKER_HEALTH_CHECK_INTERVAL = int(os.environ.get("TRACKER_HEALTH_CHECK_INTERVAL", "60"))

CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "60"))
NETHERLANDS_TZ = ZoneInfo("Europe/Amsterdam")
LISTINGS_PER_PAGE = int(os.environ.get("LISTINGS_PER_PAGE", "5"))
HIGHLIGHT_DAYS_THRESHOLD = int(os.environ.get("HIGLIGHT_DAYS_THRESHOLD", "2"))


# --- Налаштування логування ---


# 1. Створюємо основний логер
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Встановлюємо мінімальний рівень для логера

# 2. Створюємо обробник для запису в файл (без кольорів)
file_handler = logging.FileHandler(LOG_FILE_PATH)

# Створюємо звичайний форматер для файлу
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
file_handler.setFormatter(file_formatter)

# 3. Створюємо обробник для виводу в консоль (з кольорами)
stream_handler = logging.StreamHandler(sys.stdout)

# Створюємо кольоровий форматер для консолі
stream_formatter = ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
)
stream_handler.setFormatter(stream_formatter)

# 4. Додаємо обидва обробники до логера
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def escape_markdown_v2(text: str) -> str:
    """Екранує спеціальні символи для Telegram MarkdownV2."""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()

    @contextmanager
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        with self.get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language TEXT DEFAULT 'en',
                    is_active BOOLEAN DEFAULT TRUE,
                    timezone TEXT,
                    use_tracker BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = [info['name'] for info in cursor.fetchall()]
            if 'use_tracker' not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN use_tracker BOOLEAN DEFAULT TRUE")
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processed_urls (id INTEGER PRIMARY KEY AUTOINCREMENT, url_key TEXT UNIQUE NOT NULL, full_url TEXT NOT NULL, postcode TEXT, city TEXT, street TEXT, houseNumber TEXT, base_price INTEGER, publication_date TEXT, closing_date TEXT, image_url TEXT, processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sent_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, url_key TEXT, sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (user_id), FOREIGN KEY (url_key) REFERENCES processed_urls (url_key))
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS donations (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER, currency TEXT, telegram_charge_id TEXT UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (user_id))
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS url_clicks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, url_key TEXT, clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, user_agent TEXT, FOREIGN KEY (user_id) REFERENCES users (user_id), FOREIGN KEY (url_key) REFERENCES processed_urls (url_key))
            ''')
            conn.commit()
            logger.info("База даних ініціалізована")

    def get_user_tracker_preference(self, user_id: int) -> bool:
        with self.get_db_connection() as conn:
            cursor = conn.execute("SELECT use_tracker FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            # Повертаємо True, якщо колонка не існує (зворотна сумісність) або якщо вона True
            return result['use_tracker'] if result and result['use_tracker'] is not None else True

    def set_user_tracker_preference(self, user_id: int, use_tracker: bool):
        with self.get_db_connection() as conn:
            conn.execute("UPDATE users SET use_tracker = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                         (use_tracker, user_id))
            conn.commit()

    def add_or_get_user(self, user_id: int, username: str = None, first_name: str = None,
                        language_code: str = 'en') -> Dict:
        with self.get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                return dict(user)

            lang_code = language_code.lower() if language_code else 'en'
            if lang_code in ('uk', 'ru'):
                user_lang = 'uk'
            elif lang_code == 'nl':
                user_lang = 'nl'
            else:
                user_lang = 'en'

            conn.execute(
                "INSERT INTO users (user_id, username, first_name, language) VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, user_lang)
            )
            conn.commit()
            cursor = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return dict(cursor.fetchone())

    # ВИПРАВЛЕНО: Повернуто відсутній метод
    def is_url_processed(self, url_key: str) -> bool:
        with self.get_db_connection() as conn:
            return conn.execute('SELECT 1 FROM processed_urls WHERE url_key = ?', (url_key,)).fetchone() is not None

    def get_user_language(self, user_id: int) -> str:
        with self.get_db_connection() as conn:
            cursor = conn.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result['language'] if result and result['language'] in TRANSLATIONS else 'en'

    def set_user_language(self, user_id: int, lang_code: str):
        with self.get_db_connection() as conn:
            conn.execute("UPDATE users SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                         (lang_code, user_id))
            conn.commit()

    def set_user_active(self, user_id: int, is_active: bool):
        with self.get_db_connection() as conn:
            conn.execute("UPDATE users SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                         (is_active, user_id))
            conn.commit()

    def get_user_status(self, user_id: int) -> bool:
        with self.get_db_connection() as conn:
            cursor = conn.execute("SELECT is_active FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result['is_active'] if result else False

    def get_active_users(self) -> List[Dict]:
        with self.get_db_connection() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE is_active = TRUE')
            return [dict(row) for row in cursor.fetchall()]

    def get_user_timezone(self, user_id: int) -> Optional[ZoneInfo]:
        with self.get_db_connection() as conn:
            cursor = conn.execute('SELECT timezone FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            if result and result['timezone']:
                try:
                    return ZoneInfo(result['timezone'])
                except ZoneInfoNotFoundError:
                    return None
            return None

    def add_processed_url(self, **kwargs):
        with self.get_db_connection() as conn:
            conn.execute('''INSERT OR IGNORE INTO processed_urls (url_key, full_url, postcode, city, street, houseNumber, base_price, publication_date, closing_date, image_url) VALUES (:url_key, :full_url, :postcode, :city, :street, :houseNumber, :base_price, :publication_date, :closing_date, :image_url)''',
                         kwargs)
            conn.commit()

    def add_sent_message(self, user_id: int, url_key: str):
        with self.get_db_connection() as conn:
            conn.execute('INSERT INTO sent_messages (user_id, url_key) VALUES (?, ?)', (user_id, url_key))
            conn.commit()

    def add_donation(self, user_id: int, amount: int, currency: str, charge_id: str):
        with self.get_db_connection() as conn:
            conn.execute("INSERT INTO donations (user_id, amount, currency, telegram_charge_id) VALUES (?, ?, ?, ?)",
                         (user_id, amount, currency, charge_id))
            conn.commit()

    def get_listings(self, view_type: str, sort_order: str = 'newest', limit: int = 5, offset: int = 0) -> List[Dict]:
        base_query = "SELECT * FROM processed_urls"
        if view_type == 'recent':
            three_days_ago = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            where_clause = "WHERE publication_date >= ?"
            params = [three_days_ago]
        elif view_type == 'active':
            now_iso = datetime.now(timezone.utc).isoformat()
            where_clause = "WHERE closing_date > ?"
            params = [now_iso]
        else:
            return []
        order_clause = "ORDER BY closing_date ASC" if sort_order == 'closing' else "ORDER BY publication_date DESC"
        limit_clause = "LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        full_query = f"{base_query} {where_clause} {order_clause} {limit_clause}"
        with self.get_db_connection() as conn:
            cursor = conn.execute(full_query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_listings_count(self, view_type: str) -> int:
        base_query = "SELECT COUNT(id) FROM processed_urls"
        if view_type == 'recent':
            three_days_ago = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            where_clause = "WHERE publication_date >= ?"
            params = [three_days_ago]
        elif view_type == 'active':
            now_iso = datetime.now(timezone.utc).isoformat()
            where_clause = "WHERE closing_date > ?"
            params = [now_iso]
        else:
            return 0
        full_query = f"{base_query} {where_clause}"
        with self.get_db_connection() as conn:
            cursor = conn.execute(full_query, tuple(params))
            result = cursor.fetchone()
            return result[0] if result else 0


class WHBot:
    def __init__(self, token: str, db_path: str):
        self.token = token
        self.db = DatabaseManager(db_path)
        self.app = Application.builder().token(token).build()
        self.job_queue = self.app.job_queue
        self.is_tracker_healthy = True
        self.setup_handlers()

    async def check_tracker_health(self, context: ContextTypes.DEFAULT_TYPE):
        if not TRACKER_BASE_URL:
            if self.is_tracker_healthy:
                self.is_tracker_healthy = False
                logger.warning("TRACKER_BASE_URL не встановлено. Трекінг вимкнено.")
            return

        try:
            # Використовуємо простий HEAD запит, щоб не завантажувати сторінку
            health_check_url = f"{TRACKER_BASE_URL.rstrip('/')}/health"
            response = requests.get(health_check_url, timeout=5)
            response.raise_for_status()
            if not self.is_tracker_healthy:
                logger.info("Сервіс трекінгу відновив роботу.")
            self.is_tracker_healthy = True
        except requests.RequestException as e:
            if self.is_tracker_healthy:
                logger.warning(f"Сервіс трекінгу недоступний: {e}. Перемикаюсь на прямі посилання.")
            self.is_tracker_healthy = False


    def _get_final_url(self, user_id: int, listing_data: Dict) -> str:
        """Повертає URL для трекінгу або прямий URL залежно від налаштувань та стану трекера."""
        user_wants_tracking = self.db.get_user_tracker_preference(user_id)
        
        if self.is_tracker_healthy and user_wants_tracking:
            return f"{TRACKER_BASE_URL}/track?user_id={user_id}&url_key={listing_data['url_key']}"
        else:
            return listing_data['full_url']
        
    def get_text(self, user_id: int, key: str, **kwargs) -> str:
        lang = self.db.get_user_language(user_id)
        text = TRANSLATIONS.get(lang, {}).get(key)
        if not text:
            text = TRANSLATIONS['en'].get(key, f"_{key}_")
        return text.format(**kwargs)

    def get_main_keyboard(self, user_id: int) -> ReplyKeyboardMarkup:
        keyboard = [
            [self.get_text(user_id, 'main_menu_view_listings')],
            [self.get_text(user_id, 'main_menu_donate'), self.get_text(user_id, 'main_menu_settings')],
            [self.get_text(user_id, 'main_menu_help')]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(PreCheckoutQueryHandler(self.pre_checkout_callback))
        self.app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, self.successful_payment_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_buttons))

    async def handle_text_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        text = update.message.text

        if text == self.get_text(user_id, 'main_menu_view_listings'):
            await self.show_listings_command(update, context)
        elif text == self.get_text(user_id, 'main_menu_donate'):
            await self.donate_command(update, context)
        elif text == self.get_text(user_id, 'main_menu_settings'):
            await self.settings_command(update, context)
        elif text == self.get_text(user_id, 'main_menu_help'):
            await self.help_command(update, context)
        else:
            await update.message.reply_text(self.get_text(user_id, 'unknown_command'), parse_mode='MarkdownV2')

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db_user = self.db.add_or_get_user(user.id, user.username, user.first_name, user.language_code)

        is_first_time = db_user['created_at'] == db_user['updated_at']
        text_key = 'welcome_first_time' if is_first_time else 'welcome_back'
        text = self.get_text(user.id, text_key)

        await update.message.reply_text(
            text,
            reply_markup=self.get_main_keyboard(user.id),
            parse_mode='MarkdownV2'
        )

    async def show_listings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._send_paginated_listings(update.message, 'recent', 'newest', 0)

    async def donate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        amounts = [100, 300, 500, 1000]
        keyboard = [
            [InlineKeyboardButton(self.get_text(user_id, 'donate_option', amount=a), callback_data=f"donate:{a}") for
             a in amounts[:2]],
            [InlineKeyboardButton(self.get_text(user_id, 'donate_option', amount=a), callback_data=f"donate:{a}") for
             a in amounts[2:]]
        ]
        await update.message.reply_text(
            self.get_text(user_id, 'donate_menu_title'),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MarkdownV2'
        )

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._send_settings_menu(update.message.chat_id, context)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        text = self.get_text(user_id, 'help_text', interval=CHECK_INTERVAL)
        await update.message.reply_text(text, parse_mode='MarkdownV2')

    async def _send_settings_menu(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE, query: Optional[CallbackQuery] = None):
        user_id = chat_id
        is_subscribed = self.db.get_user_status(user_id)
        use_tracker = self.db.get_user_tracker_preference(user_id)
        
        sub_button_text = self.get_text(user_id, 'settings_unsubscribe' if is_subscribed else 'settings_subscribe')
        tracker_button_text = self.get_text(user_id, 'settings_disable_tracker' if use_tracker else 'settings_enable_tracker')
        timezone_url = f"{TRACKER_BASE_URL}/get_tz?user_id={user_id}"

        keyboard = [
            [InlineKeyboardButton(sub_button_text, callback_data="toggle_subscription")],
            [InlineKeyboardButton(tracker_button_text, callback_data="toggle_tracker")],
            [InlineKeyboardButton(self.get_text(user_id, 'settings_set_timezone'), url=timezone_url)],
            [InlineKeyboardButton(self.get_text(user_id, 'settings_change_language'), callback_data="show_lang_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = self.get_text(user_id, 'settings_menu_title')

        if query:
            try:
                await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='MarkdownV2')
            except telegram.error.BadRequest as e:
                if "Message is not modified" not in str(e): logger.error(f"Error editing settings menu: {e}")
        else:
            await context.bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode='MarkdownV2')

    async def _send_lang_menu(self, query: CallbackQuery):
        user_id = query.from_user.id
        keyboard = [
            [InlineKeyboardButton(TRANSLATIONS['uk']['lang_uk'], callback_data="set_lang:uk")],
            [InlineKeyboardButton(TRANSLATIONS['en']['lang_en'], callback_data="set_lang:en")],
            [InlineKeyboardButton(TRANSLATIONS['nl']['lang_nl'], callback_data="set_lang:nl")],
            [InlineKeyboardButton(self.get_text(user_id, 'back_to_settings'),
                                  callback_data="show_settings_menu")]
        ]
        await query.edit_message_text(
            self.get_text(user_id, 'lang_menu_title'),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MarkdownV2'
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = query.from_user.id

        if data == self.get_text(user_id, 'data_placeholder'):
            return

        if data == "show_lang_menu":
            await self._send_lang_menu(query)
            return

        if data == "show_settings_menu":
            await self._send_settings_menu(user_id, context, query=query)
            return
        if data == "toggle_tracker":
            current_pref = self.db.get_user_tracker_preference(user_id)
            self.db.set_user_tracker_preference(user_id, not current_pref)
            await query.answer(self.get_text(user_id, 'tracker_status_changed_alert'), show_alert=True)
            await self._send_settings_menu(user_id, context, query=query)
            return
        if data.startswith("set_lang:"):
            lang_code = data.split(':')[1]
            if lang_code in TRANSLATIONS:
                self.db.set_user_language(user_id, lang_code)
                lang_name = TRANSLATIONS[lang_code][f'lang_{lang_code}']
                await query.answer(self.get_text(user_id, 'lang_changed_alert', lang_name=lang_name), show_alert=True)
                await self._send_settings_menu(user_id, context, query=query)
                await context.bot.send_message(
                    user_id,
                    self.get_text(user_id, 'welcome_back'),
                    reply_markup=self.get_main_keyboard(user_id),
                    parse_mode='MarkdownV2'
                )
            return

        if data == "toggle_subscription":
            is_currently_subscribed = self.db.get_user_status(user_id)
            new_status = not is_currently_subscribed
            self.db.set_user_active(user_id, new_status)
            alert_text = self.get_text(user_id, 'toggled_subscribe_ok' if new_status else 'toggled_unsubscribe_ok')
            await query.answer(alert_text, show_alert=True)
            await self._send_settings_menu(user_id, context, query=query)
            return

        if data.startswith("donate:"):
            try:
                amount = int(data.split(':')[1])
                await self.send_invoice(user_id, amount)
            except (IndexError, ValueError):
                logger.warning(f"Invalid donate callback data: {data}")
            return

        try:
            view_type, sort_order, page_str = data.split(':')
            page = int(page_str)
            await self._edit_paginated_listings(query, view_type, sort_order, page)
        except (ValueError, IndexError):
            logger.warning(f"Invalid pagination callback data: {data}")

    async def _send_paginated_listings(self, message: Message, view_type: str, sort_order: str, page: int):
        user_id = message.from_user.id
        offset = page * LISTINGS_PER_PAGE
        listings = self.db.get_listings(view_type, sort_order, LISTINGS_PER_PAGE, offset)
        total_listings = self.db.get_listings_count(view_type)

        if not listings:
            no_listings_key = 'no_recent_listings' if view_type == 'recent' else 'no_active_listings'
            await message.reply_text(self.get_text(user_id, no_listings_key))
            return

        text, reply_markup = self._generate_listings_view(user_id, listings, total_listings, page, sort_order,
                                                          view_type)
        await message.reply_text(text, reply_markup=reply_markup, parse_mode='MarkdownV2')

    async def _edit_paginated_listings(self, query: CallbackQuery, view_type: str, sort_order: str, page: int):
        user_id = query.from_user.id
        offset = page * LISTINGS_PER_PAGE
        listings = self.db.get_listings(view_type, sort_order, LISTINGS_PER_PAGE, offset)
        total_listings = self.db.get_listings_count(view_type)
        text, reply_markup = self._generate_listings_view(user_id, listings, total_listings, page, sort_order,
                                                          view_type)

        try:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='MarkdownV2')
        except telegram.error.BadRequest as e:
            if "Message is not modified" not in str(e):
                logger.error(f"Error editing paginated listings: {e}")

    def _generate_listings_view(self, user_id: int, listings: List[Dict], total_listings: int, page: int,
                                sort_order: str, view_type: str) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        if not listings:
            key = 'no_recent_listings' if view_type == 'recent' else 'no_active_listings'
            return self.get_text(user_id, key), None

        message_parts = []
        for listing in listings:
            title, body = self._prepare_listing_text(user_id, listing)
            time_left_text = self._format_time_left(user_id, listing.get('closing_date'))
            full_listing_text = f"**{title}**\n{body}"
            if time_left_text:
                full_listing_text += f"\n{time_left_text}"
            message_parts.append(full_listing_text)

        full_text = "\n\n\\-\\-\\-\n\n".join(message_parts)
        total_pages = (total_listings + LISTINGS_PER_PAGE - 1) // LISTINGS_PER_PAGE or 1
        keyboard = []

        newest_text, closing_text, placeholder = self.get_text(user_id, 'sort_by_newest'), self.get_text(user_id, 'sort_by_closing_date'), self.get_text(user_id, 'data_placeholder')
        sort_buttons = [
            InlineKeyboardButton(f"✅ {newest_text}",
                                 callback_data=placeholder) if sort_order == 'newest' else InlineKeyboardButton(
                newest_text, callback_data=f"{view_type}:newest:0"),
            InlineKeyboardButton(f"✅ {closing_text}",
                                 callback_data=placeholder) if sort_order == 'closing' else InlineKeyboardButton(
                closing_text, callback_data=f"{view_type}:closing:0")
        ]
        keyboard.append(sort_buttons)

        if total_pages > 1:
            nav_buttons = [
                InlineKeyboardButton("⬅️",
                                     callback_data=f"{view_type}:{sort_order}:{page - 1}") if page > 0 else InlineKeyboardButton(
                    " ", callback_data=placeholder),
                InlineKeyboardButton(self.get_text(user_id, 'page_info', page=page + 1, total_pages=total_pages),
                                     callback_data=placeholder),
                InlineKeyboardButton("➡️",
                                     callback_data=f"{view_type}:{sort_order}:{page + 1}") if page < total_pages - 1 else InlineKeyboardButton(
                    " ", callback_data=placeholder)
            ]
            keyboard.append(nav_buttons)

        switch_text, switch_callback = (
            self.get_text(user_id, 'go_to_active'), f"active:{sort_order}:0") if view_type == 'recent' else (
            self.get_text(user_id, 'go_to_recent'), f"recent:{sort_order}:0")
        keyboard.append([InlineKeyboardButton(switch_text, callback_data=switch_callback)])

        return full_text, InlineKeyboardMarkup(keyboard)

    def _prepare_listing_text(self, user_id: int, listing_data: Dict, include_link_in_body: bool = True) -> Tuple[
        str, str]:
        not_specified_text = self.get_text(user_id, 'not_specified')
        safe_address = {k: escape_markdown_v2(listing_data.get(k) or not_specified_text) for k in
                        ['postcode', 'city', 'street', 'houseNumber']}
        title = self.get_text(user_id, 'new_listing_title', **safe_address)

        pub_date = self.format_date_for_user(user_id, listing_data.get('publication_date'))
        close_date = self.format_date_for_user(user_id, listing_data.get('closing_date'))

        body_data = {
            'base_price': escape_markdown_v2(listing_data.get('base_price') or not_specified_text),
            'publication_date': escape_markdown_v2(pub_date),
            'closing_date': escape_markdown_v2(close_date)
        }
        body = self.get_text(user_id, 'new_listing_body', **body_data)

        if include_link_in_body:
            # Використовуємо новий метод для отримання URL
            final_url = self._get_final_url(user_id, listing_data)
            view_button_text = self.get_text(user_id, 'view_listing_button')
            body += f"\n[{escape_markdown_v2(view_button_text)}]({final_url})"

        return title, body

    def _format_time_left(self, user_id: int, closing_date_str: str) -> Optional[str]:
        if not closing_date_str: return None
        try:
            now = datetime.now(timezone.utc)
            closing_dt = datetime.fromisoformat(closing_date_str.replace('Z', '+00:00'))
            if closing_dt <= now: return None

            time_left = closing_dt - now
            if time_left.days >= HIGHLIGHT_DAYS_THRESHOLD: return None

            if time_left.days > 0:
                return self.get_text(user_id, 'listing_expires_in_days', days=f"**`{time_left.days}`**")

            hours_left = int(time_left.total_seconds() / 3600)
            if hours_left > 0:
                return self.get_text(user_id, 'listing_expires_in_hours', hours=f"**`{hours_left}`**")

            return self.get_text(user_id, 'listing_expires_today')
        except (ValueError, TypeError):
            return None

    def format_date_for_user(self, user_id: int, date_str: str) -> str:
        if not date_str:
            return self.get_text(user_id, 'not_specified')
        try:
            user_tz = self.db.get_user_timezone(user_id) or NETHERLANDS_TZ
            dt_utc = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt_utc.astimezone(user_tz).strftime('%d.%m.%Y %H:%M')
        except (ValueError, TypeError):
            return date_str

    async def send_invoice(self, user_id: int, amount: int):
        title = self.get_text(user_id, 'donate_invoice_title')
        description = self.get_text(user_id, 'donate_invoice_description')
        payload = f"whbot-donation-{user_id}-{int(time.time())}"

        await self.app.bot.send_invoice(
            chat_id=user_id, title=title, description=description, payload=payload,
            provider_token=PROVIDER_TOKEN, currency="XTR", prices=[LabeledPrice(title, amount)]
        )

    async def pre_checkout_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.pre_checkout_query
        if query.total_amount < 1:
            await query.answer(ok=False, error_message="Something went wrong...")
        else:
            await query.answer(ok=True)

    async def successful_payment_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        payment_info = update.message.successful_payment
        self.db.add_donation(
            user_id=user_id, amount=payment_info.total_amount,
            currency=payment_info.currency, charge_id=payment_info.telegram_payment_charge_id
        )
        await update.message.reply_text(self.get_text(user_id, 'payment_successful'))

    async def send_listing_message(self, user_id: int, listing_data: Dict):
        url_key = listing_data['url_key']
        title, body = self._prepare_listing_text(user_id, listing_data, include_link_in_body=False)
        message_text = f"**{title}**\n\n{body}"

        final_url = self._get_final_url(user_id, listing_data)
        keyboard = [[InlineKeyboardButton(self.get_text(user_id, 'view_listing_button'), url=final_url)]]
        image_url = listing_data.get('image_url')
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            if image_url:
                await self.app.bot.send_photo(chat_id=user_id, photo=image_url, caption=message_text,
                                              reply_markup=reply_markup, parse_mode='MarkdownV2')
            else:
                await self.app.bot.send_message(chat_id=user_id, text=message_text, reply_markup=reply_markup,
                                                parse_mode='MarkdownV2')
            return True
        except Exception as e:
            logger.error(f"Error sending notification to {user_id} for {url_key}: {e}")
            if image_url:
                try:
                    logger.warning(f"Retrying notification for {url_key} as text after photo failure.")
                    await self.app.bot.send_message(chat_id=user_id, text=message_text, reply_markup=reply_markup,
                                                    parse_mode='MarkdownV2')
                    return True
                except Exception as inner_e:
                    logger.error(f"Failed to send notification as text as well: {inner_e}")
            return False

    def fetch_json_data(self, page: int = 0) -> Optional[Dict]:
        try:
            response = requests.get(API_URL, params={'limit': 100, 'page': page}, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    async def process_new_listings(self, context: ContextTypes.DEFAULT_TYPE):
        logger.info("Starting new listings processing cycle.")
        active_users = self.db.get_active_users()
        if not active_users:
            logger.info("No active users, skipping processing cycle.")
            return

        page = 0
        while True:
            data = self.fetch_json_data(page)
            if not data or not data.get('data'):
                break

            for item in data['data']:
                url_key = item.get('urlKey')
                if not url_key or self.db.is_url_processed(url_key):
                    continue

                image_url = (IMAGE_BASE_URL + uri) if (pictures := item.get('pictures', [])) and (
                            uri := pictures[0].get('uri')) else None
                house_addition = item.get('houseNumberAddition', '') or ''

                listing_data = {
                    'url_key': url_key, 'full_url': BASE_URL + url_key, 'postcode': item.get('postalcode'),
                    'city': item.get('gemeenteGeoLocatieNaam'), 'street': item.get('street'),
                    'houseNumber': f"{item.get('houseNumber', '')}{house_addition}",
                    'base_price': item.get('netRent'),
                    'publication_date': item.get('publicationDate'), 'closing_date': item.get('closingDate'),
                    'image_url': image_url
                }

                self.db.add_processed_url(**listing_data)
                logger.info(f"Found new listing: {url_key}")

                for user in active_users:
                    try:
                        if await self.send_listing_message(user['user_id'], listing_data):
                            self.db.add_sent_message(user['user_id'], url_key)
                        await asyncio.sleep(0.1)  # Throttling
                    except Exception as e:
                        logger.error(f"Unhandled exception in user notification loop for user {user['user_id']}: {e}")


            metadata = data.get('_metadata', {})
            if metadata.get('page', 0) < metadata.get('page_count', 1) - 1:
                page += 1
                await asyncio.sleep(1)
            else:
                break
        logger.info("Finished listings processing cycle.")

    def run(self):
        logger.info("🚀 Starting WH Bot")
        # Запускаємо основний процес
        self.job_queue.run_repeating(self.process_new_listings, interval=CHECK_INTERVAL, first=10)
        logger.info(f"Listings monitoring started with an interval of {CHECK_INTERVAL} seconds.")
        # Запускаємо процес перевірки здоров'я трекера
        self.job_queue.run_repeating(self.check_tracker_health, interval=TRACKER_HEALTH_CHECK_INTERVAL, first=5)
        logger.info(f"Tracker health check started with an interval of {TRACKER_HEALTH_CHECK_INTERVAL} seconds.")
        
        self.app.run_polling()


if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        logger.critical("FATAL: TELEGRAM_BOT_TOKEN is not set! Exiting.")
        sys.exit(1)
    if not PROVIDER_TOKEN:
        logger.warning("PROVIDER_TOKEN is not set! Donation feature will not work.")

    bot = WHBot(TELEGRAM_BOT_TOKEN, DATABASE_PATH)
    bot.run()
