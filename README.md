# WHx Bot README

<div align="center">
<a href="#ukrainian">Українська</a> • <a href="#english">English</a> • <a href="#nederlands">Nederlands</a>
</div>

---

<a name="ukrainian"></a>

## 🇺🇦 WHx Bot (Українська)

**WHx Bot** — це багатофункціональний Telegram-бот, створений для відстеження та сповіщення про нові оголошення оренди на нідерландському сайті `woninghuren.nl`. Бот підтримує кілька мов, дозволяє гнучко налаштовувати сповіщення та часовий пояс, а також включає аналітичний мікросервіс для відстеження переходів за посиланнями.

### 🚀 Ключові можливості

*   **Миттєві сповіщення:** Бот періодично перевіряє API на наявність нових оголошень і надсилає їх активним користувачам.
*   **Багатомовний інтерфейс:** Повна підтримка української, англійської та нідерландської мов.
*   **Гнучкі налаштування:** Користувачі можуть вмикати/вимикати сповіщення, змінювати мову та налаштовувати відстеження посилань.
*   **Автоматичне визначення часового поясу:** Інтерактивна веб-сторінка для налаштування часового поясу користувача.
*   **Перегляд оголошень:** Вбудований функціонал для перегляду активних та нещодавніх оголошень з сортуванням та пагінацією.
*   **Система донатів:** Можливість підтримати розробника через Telegram Stars.

### 📂 Структура файлів

| Файл                | Опис                                                                                                                                                                                                                                                                  |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`           | **Основний файл бота.** Містить логіку, що відповідає за роботу з Telegram API (`python-telegram-bot`). Обробляє команди, керує станом користувачів (мова, підписки) у базі даних SQLite, запускає періодичні завдання для перевірки оголошень та надсилає сповіщення. |
| `tracker.py`        | **Аналітичний мікросервіс на FastAPI.** Створює веб-сервер, який виконує дві основні функції: 1) Відстежує кліки за посиланнями на оголошення для збору статистики. 2) Надає веб-сторінку для автоматичного визначення та збереження часового поясу користувача.    |
| `i18n.py`           | **Файл інтернаціоналізації (i18n).** Містить словник `TRANSLATIONS` з усіма текстовими рядками, що використовуються в боті, перекладеними на українську, англійську та нідерландську мови. Це централізує тексти та спрощує додавання нових мов.         |
| `requirements.txt`  | Перелік усіх Python-бібліотек, необхідних для роботи проєкту (`python-telegram-bot`, `fastapi`, `requests` тощо). Встановлюється командою `pip install -r requirements.txt`.                                                                                      |
| `.env-template`     | **Шаблон файлу конфігурації.** Містить список усіх змінних середовища, які необхідні для запуску бота та трекера (токени, шляхи до файлів, URL-адреси).                                                                                                                     |

### 🛠️ Як використовувати

Проєкт складається з двох окремих сервісів: основного бота та трекера. Їх потрібно запускати паралельно.

1.  **Клонуйте репозиторій:**
    ```bash
    git clone https://github.com/arkk4/whx_bot.git
    cd whx_bot
    ```

2.  **Встановіть залежності:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Налаштуйте змінні середовища:**
    *   Створіть файл `.env` на основі `.env-template`.
    *   Заповніть усі необхідні змінні, такі як `TELEGRAM_BOT_TOKEN`, `PROVIDER_TOKEN`, `DATABASE_PATH`, `API_URL` тощо.
    *   `TRACKER_BASE_URL` має вказувати на адресу, де буде запущено сервіс `tracker.py` (наприклад, `http://localhost:8000`).

4.  **Запустіть трекер:**
    Відкрийте один термінал та запустіть веб-сервіс трекера за допомогою Uvicorn:
    ```bash
    uvicorn tracker:app --host 0.0.0.0 --port 8000
    ```

5.  **Запустіть основного бота:**
    Відкрийте другий термінал та запустіть бота:
    ```bash
    python main.py
    ```
    Після цього бот буде онлайн і готовий до роботи.

### ✅ TODO

*   [ ] **Локалізація сторінки трекера:** Додати підтримку кількох мов для HTML-сторінки встановлення часового поясу в `tracker.py`, використовуючи параметри запиту.
*   [ ] **Рефакторинг коментарів:** Переписати коментарі та повідомлення логера в коді на англійську мову для відповідності міжнародним стандартам розробки.
*   [ ] **Розширене тестування:** Написати unit-тести для `DatabaseManager` та ключових функцій бота для забезпечення стабільності.
*   [ ] **Обробка помилок:** Покращити обробку можливих помилок від API та сервісу трекера.

---

<a name="english"></a>

## 🇬🇧 WHx Bot (English)

**WHx Bot** is a multifunctional Telegram bot designed to track and notify about new rental listings on the Dutch website `woninghuren.nl`. The bot supports multiple languages, allows flexible configuration of notifications and time zones, and includes an analytics microservice for tracking link clicks.

### 🚀 Key Features

*   **Instant Notifications:** The bot periodically checks an API for new listings and sends them to active users.
*   **Multilingual Interface:** Full support for Ukrainian, English, and Dutch.
*   **Flexible Settings:** Users can enable/disable notifications, change the language, and manage link tracking.
*   **Automatic Time Zone Detection:** An interactive web page for setting the user's time zone.
*   **Listing Browser:** Built-in functionality to view active and recent listings with sorting and pagination.
*   **Donation System:** Ability to support the developer via Telegram Stars.

### 📂 File Structure

| File                | Description                                                                                                                                                                                                                                                           |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`           | **The main bot file.** Contains the logic for interacting with the Telegram API (`python-telegram-bot`). It handles commands, manages user state (language, subscriptions) in an SQLite database, runs periodic jobs to check for listings, and sends notifications. |
| `tracker.py`        | **An analytics microservice using FastAPI.** It creates a web server with two main functions: 1) Tracking clicks on listing links for statistical purposes. 2) Providing a web page to automatically detect and save the user's time zone.                             |
| `i18n.py`           | **Internationalization (i18n) file.** Contains the `TRANSLATIONS` dictionary with all text strings used in the bot, translated into Ukrainian, English, and Dutch. This centralizes texts and simplifies adding new languages.                                        |
| `requirements.txt`  | A list of all Python libraries required for the project (`python-telegram-bot`, `fastapi`, `requests`, etc.). Install with `pip install -r requirements.txt`.                                                                                                          |
| `.env-template`     | **Configuration file template.** Contains a list of all environment variables needed to run the bot and the tracker (tokens, file paths, URLs).                                                                                                                         |

### 🛠️ How to Use

The project consists of two separate services: the main bot and the tracker. They need to be run in parallel.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/arkk4/whx_bot.git
    cd whx_bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    *   Create a `.env` file from the `.env-template`.
    *   Fill in all the required variables, such as `TELEGRAM_BOT_TOKEN`, `PROVIDER_TOKEN`, `DATABASE_PATH`, `API_URL`, etc.
    *   `TRACKER_BASE_URL` should point to the address where the `tracker.py` service will run (e.g., `http://localhost:8000`).

4.  **Run the tracker:**
    Open one terminal and run the tracker web service using Uvicorn:
    ```bash
    uvicorn tracker:app --host 0.0.0.0 --port 8000
    ```

5.  **Run the main bot:**
    Open a second terminal and run the bot:
    ```bash
    python main.py
    ```
    The bot will now be online and ready to work.

### ✅ TODO

*   [ ] **Localize Tracker Page:** Add multi-language support to the time zone setting HTML page in `tracker.py` using query parameters.
*   [ ] **Refactor Comments:** Rewrite comments and logger messages in the code to English to align with international development standards.
*   [ ] **Enhanced Testing:** Write unit tests for the `DatabaseManager` and key bot functions to ensure stability.
*   [ ] **Error Handling:** Improve the handling of potential errors from the API and tracker service.

---

<a name="nederlands"></a>

## 🇳🇱 WHx Bot (Nederlands)

**WHx Bot** is een multifunctionele Telegram-bot die is ontworpen om nieuwe huuradvertenties op de Nederlandse website `woninghuren.nl` te volgen en erover te informeren. De bot ondersteunt meerdere talen, maakt flexibele configuratie van meldingen en tijdzones mogelijk, en bevat een analytische microservice voor het bijhouden van link-klikken.

### 🚀 Belangrijkste Kenmerken

*   **Directe Meldingen:** De bot controleert periodiek een API op nieuwe advertenties en stuurt deze naar actieve gebruikers.
*   **Meertalige Interface:** Volledige ondersteuning voor Oekraïens, Engels en Nederlands.
*   **Flexibele Instellingen:** Gebruikers kunnen meldingen in- of uitschakelen, de taal wijzigen en het volgen van links beheren.
*   **Automatische Tijdzone Detectie:** Een interactieve webpagina voor het instellen van de tijdzone van de gebruiker.
*   **Advertenties Bekijken:** Ingebouwde functionaliteit om actieve en recente advertenties te bekijken met sortering en paginering.
*   **Donatiesysteem:** Mogelijkheid om de ontwikkelaar te steunen via Telegram Stars.

### 📂 Bestandsstructuur

| Bestand             | Beschrijving                                                                                                                                                                                                                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`           | **Het hoofdbestand van de bot.** Bevat de logica voor interactie met de Telegram API (`python-telegram-bot`). Het verwerkt commando's, beheert de gebruikersstatus (taal, abonnementen) in een SQLite-database, voert periodieke taken uit om advertenties te controleren en stuurt meldingen. |
| `tracker.py`        | **Een analytische microservice met FastAPI.** Het creëert een webserver met twee hoofdfuncties: 1) Het bijhouden van klikken op advertentielinks voor statistische doeleinden. 2) Het aanbieden van een webpagina om automatisch de tijdzone van de gebruiker te detecteren en op te slaan. |
| `i18n.py`           | **Internationalisatie (i18n) bestand.** Bevat de `TRANSLATIONS` dictionary met alle tekststrings die in de bot worden gebruikt, vertaald naar het Oekraïens, Engels en Nederlands. Dit centraliseert teksten en vereenvoudigt het toevoegen van nieuwe talen.          |
| `requirements.txt`  | Een lijst van alle Python-bibliotheken die nodig zijn voor het project (`python-telegram-bot`, `fastapi`, `requests`, enz.). Te installeren met `pip install -r requirements.txt`.                                                                                    |
| `.env-template`     | **Configuratiebestand sjabloon.** Bevat een lijst van alle omgevingsvariabelen die nodig zijn om de bot en de tracker te draaien (tokens, bestandspaden, URL's).                                                                                                      |

### 🛠️ Hoe te Gebruiken

Het project bestaat uit twee afzonderlijke services: de hoofdbot en de tracker. Ze moeten parallel worden uitgevoerd.

1.  **Kloon de repository:**
    ```bash
    git clone https://github.com/arkk4/whx_bot.git
    cd whx_bot
    ```

2.  **Installeer de afhankelijkheden:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Stel de omgevingsvariabelen in:**
    *   Maak een `.env`-bestand aan op basis van `.env-template`.
    *   Vul alle vereiste variabelen in, zoals `TELEGRAM_BOT_TOKEN`, `PROVIDER_TOKEN`, `DATABASE_PATH`, `API_URL`, etc.
    *   `TRACKER_BASE_URL` moet verwijzen naar het adres waar de `tracker.py`-service zal draaien (bijv. `http://localhost:8000`).

4.  **Start de tracker:**
    Open een terminal en start de tracker-webservice met Uvicorn:
    ```bash
    uvicorn tracker:app --host 0.0.0.0 --port 8000
    ```

5.  **Start de hoofdbot:**
    Open een tweede terminal en start de bot:
    ```bash
    python main.py
    ```
    De bot is nu online en klaar voor gebruik.

### ✅ TODO

*   [ ] **Tracker-pagina Lokaliseren:** Voeg meertalige ondersteuning toe aan de HTML-pagina voor tijdzone-instelling in `tracker.py` met behulp van queryparameters.
*   [ ] **Commentaar Refactoren:** Herschrijf opmerkingen en logberichten in de code naar het Engels om te voldoen aan internationale ontwikkelingsnormen.
*   [ ] **Uitgebreid Testen:** Schrijf unit-tests voor de `DatabaseManager` en belangrijke botfuncties om de stabiliteit te garanderen.
*   [ ] **Foutafhandeling:** Verbeter de afhandeling van mogelijke fouten van de API en de tracker-service.
