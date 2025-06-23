# i18n.py

TRANSLATIONS = {
    'uk': {
        # --- Меню та загальні ---
        'welcome_first_time': (
            "🏠 **Вітаємо у WHx Bot\\!**\n\n"
            "Цей бот допоможе вам не пропустити нові оголошення про оренду на `woninghuren\\.nl`\\.\n\n"
            "✅ За замовчуванням, ви вже **підписані** на отримання сповіщень\\. Ви можете змінити це в будь\\-який час у **⚙️ Налаштуваннях**\\.\n\n"
            "Для правильного відображення часу, будь ласка, встановіть свій часовий пояс також у налаштуваннях\\."
        ),
        'welcome_back': "🏠 Головне меню\\. Чим можу допомогти\\?",
        'main_menu_view_listings': "📄 Переглянути оголошення",
        'main_menu_donate': "💖 Підтримати",
        'main_menu_settings': "⚙️ Налаштування",
        'main_menu_help': "❓ Довідка",
        'unknown_command': "🤔 Незрозуміла команда\\. Будь ласка, використовуйте кнопки меню\\.",
        'not_specified': "Не вказано",
        'data_placeholder': "noop",

        # --- Підписка ---
        'toggled_subscribe_ok': "✅ Ви успішно підписались на сповіщення!",
        'toggled_unsubscribe_ok': "⏹ Ви відписались від сповіщень.",

        # --- Налаштування ---
        'settings_menu_title': "⚙️ **Налаштування**\n\nТут ви можете керувати підпискою, встановити свій часовий пояс, змінити мову бота та керувати трекінгом посилань\\.",
        'settings_set_timezone': "🕒 Встановити часовий пояс",
        'settings_subscribe': "🔔 Підписатись на сповіщення",
        'settings_unsubscribe': "🔕 Відписатись від сповіщень",
        'settings_change_language': "🌐 Змінити мову",
        'settings_enable_tracker': "🛰️ Увімкнути трекінг посилань",
        'settings_disable_tracker': "🛰️ Вимкнути трекінг посилань",
        'tracker_status_changed_alert': "✅ Статус трекінгу оновлено!",
        
        # --- Мова ---
        'lang_menu_title': "🌐 **Оберіть мову**",
        'lang_uk': "🇺🇦 Українська",
        'lang_en': "🇬🇧 English",
        'lang_nl': "🇳🇱 Nederlands",
        'back_to_settings': "⬅️ Назад до налаштувань",
        'lang_changed_alert': "✅ Мову змінено на {lang_name}!",

        # --- Донати ---
        'donate_menu_title': "💖 **Підтримати розробку**\n\nВаша підтримка у вигляді Telegram Stars допомагає боту працювати стабільно та розвиватися\\. Оберіть зручну для вас суму:",
        'donate_option': "{amount} ⭐",
        'donate_invoice_title': "Підтримка розробки WH Bot",
        'donate_invoice_description': "Ваші зірки допоможуть боту розвиватися та працювати стабільно\\. Дякую\\!",
        'payment_successful': "🎉 Дуже дякую за підтримку\\! Ваші зірки отримано\\.",
        
        # --- Оголошення ---
        'new_listing_title': "🏠 {postcode} {city}, {street} {houseNumber}",
        'new_listing_body': "💰 Ціна: {base_price} €\n📅 Дата публікації: {publication_date}\n⏳ Діє до: {closing_date}",
        'view_listing_button': "👀 Переглянути деталі",
        'no_recent_listings': "😕 За останні 3 дні не було нових оголошень\\.",
        'no_active_listings': "😕 Наразі немає активних оголошень\\.",
        'listing_expires_in_days': "⏳ Закінчується через {days} дн\\.",
        'listing_expires_in_hours': "⏳ Закінчується через {hours} год\\.",
        'listing_expires_today': "🔥 Закінчується сьогодні\\!",
        'sort_by_newest': "⬇️ Новіші",
        'sort_by_closing_date': "⏳ Закінчуються",
        'page_info': "Сторінка {page}/{total_pages}",
        'go_to_active': "Переглянути всі активні",
        'go_to_recent': "Переглянути останні",

        # --- Довідка ---
        'help_text': (
            "🤖 **Довідка по WH Bot**\n\n"
            "Керуйте ботом за допомогою кнопок внизу екрана:\n\n"
            "📄 **Переглянути оголошення** \\- показує список оголошень\\.\n\n"
            "💖 **Підтримати** \\- можливість підтримати розробника\\.\n\n"
            "⚙️ **Налаштування** \\- дозволяє керувати сповіщеннями, часовим поясом та мовою\\.\n\n"
            "Бот перевіряє наявність нових оголошень кожні {interval} секунд\\."
        ),
    },
    'en': {
        # --- Menus & General ---
        'welcome_first_time': (
            "🏠 **Welcome to WHx Bot\\!**\n\n"
            "This bot helps you not to miss new rental listings on `woninghuren\\.nl`\\.\n\n"
            "✅ By default, you are already **subscribed** to notifications\\. You can change this anytime in **⚙️ Settings**\\.\n\n"
            "For correct time display, please also set your time zone in the settings\\."
        ),
        'welcome_back': "🏠 Main menu\\. How can I help you\\?",
        'main_menu_view_listings': "📄 View Listings",
        'main_menu_donate': "💖 Support",
        'main_menu_settings': "⚙️ Settings",
        'main_menu_help': "❓ Help",
        'unknown_command': "🤔 Unrecognized command\\. Please use the menu buttons\\.",
        'not_specified': "Not specified",
        'data_placeholder': "noop",

        # --- Subscription ---
        'toggled_subscribe_ok': "✅ You have successfully subscribed to notifications!",
        'toggled_unsubscribe_ok': "⏹ You have unsubscribed from notifications.",

        # --- Settings ---
        'settings_menu_title': "⚙️ **Settings**\n\nHere you can manage your subscription, set your time zone, change the bot's language, and manage link tracking\\.",
        'settings_set_timezone': "🕒 Set Time Zone",
        'settings_subscribe': "🔔 Subscribe to notifications",
        'settings_unsubscribe': "🔕 Unsubscribe from notifications",
        'settings_change_language': "🌐 Change Language",
        'settings_enable_tracker': "🛰️ Enable link tracking",
        'settings_disable_tracker': "🛰️ Disable link tracking",
        'tracker_status_changed_alert': "✅ Tracking status updated!",
        
        # --- Language ---
        'lang_menu_title': "🌐 **Choose a language**",
        'lang_uk': "🇺🇦 Українська",
        'lang_en': "🇬🇧 English",
        'lang_nl': "🇳🇱 Nederlands",
        'back_to_settings': "⬅️ Back to Settings",
        'lang_changed_alert': "✅ Language changed to {lang_name}!",

        # --- Donations ---
        'donate_menu_title': "💖 **Support the development**\n\nYour support in the form of Telegram Stars helps the bot to run stably and evolve\\. Choose an amount that is convenient for you:",
        'donate_option': "{amount} ⭐",
        'donate_invoice_title': "Support for WH Bot Development",
        'donate_invoice_description': "Your stars will help the bot to develop and operate stably\\. Thank you\\!",
        'payment_successful': "🎉 Thank you so much for your support\\! Your stars have been received\\.",
        
        # --- Listings ---
        'new_listing_title': "🏠 {postcode} {city}, {street} {houseNumber}",
        'new_listing_body': "💰 Price: {base_price} €\n📅 Publication date: {publication_date}\n⏳ Valid until: {closing_date}",
        'view_listing_button': "👀 View Details",
        'no_recent_listings': "😕 No new listings in the last 3 days\\.",
        'no_active_listings': "😕 There are no active listings at the moment\\.",
        'listing_expires_in_days': "⏳ Expires in {days} days\\.",
        'listing_expires_in_hours': "⏳ Expires in {hours} hours\\.",
        'listing_expires_today': "🔥 Expires today\\!",
        'sort_by_newest': "⬇️ Newest",
        'sort_by_closing_date': "⏳ Ending Soon",
        'page_info': "Page {page}/{total_pages}",
        'go_to_active': "View all active",
        'go_to_recent': "View recent",

        # --- Help ---
        'help_text': (
            "🤖 **WH Bot Help**\n\n"
            "Control the bot using the buttons at the bottom of the screen:\n\n"
            "📄 **View Listings** \\- shows a list of listings\\.\n\n"
            "💖 **Support** \\- an opportunity to support the developer\\.\n\n"
            "⚙️ **Settings** \\- allows you to manage notifications, time zone, and language\\.\n\n"
            "The bot checks for new listings every {interval} seconds\\."
        ),
    },
    'nl': {
        # --- Menu's & Algemeen ---
        'welcome_first_time': (
            "🏠 **Welkom bij WHx Bot\\!**\n\n"
            "Deze bot helpt je om geen nieuwe huuradvertenties op `woninghuren\\.nl` te missen\\.\n\n"
            "✅ Standaard ben je al **geabonneerd** op meldingen\\. Je kunt dit op elk moment wijzigen in **⚙️ Instellingen**\\.\n\n"
            "Voor een correcte tijdweergave, stel ook je tijdzone in bij de instellingen\\."
        ),
        'welcome_back': "🏠 Hoofdmenu\\. Hoe kan ik je helpen\\?",
        'main_menu_view_listings': "📄 Bekijk Aanbod",
        'main_menu_donate': "💖 Ondersteunen",
        'main_menu_settings': "⚙️ Instellingen",
        'main_menu_help': "❓ Help",
        'unknown_command': "🤔 Onbekend commando\\. Gebruik alstublieft de menuknoppen\\.",
        'not_specified': "Niet opgegeven",
        'data_placeholder': "noop",

        # --- Abonnement ---
        'toggled_subscribe_ok': "✅ Je bent succesvol geabonneerd op meldingen!",
        'toggled_unsubscribe_ok': "⏹ Je hebt je afgemeld voor meldingen.",

        # --- Instellingen ---
        'settings_menu_title': "⚙️ **Instellingen**\n\nHier kun je je abonnement beheren, je tijdzone instellen, de taal van de bot wijzigen en het volgen van links beheren\\.",
        'settings_set_timezone': "🕒 Tijdzone Instellen",
        'settings_subscribe': "🔔 Abonneren op meldingen",
        'settings_unsubscribe': "🔕 Afmelden voor meldingen",
        'settings_change_language': "🌐 Taal Wijzigen",
        'settings_enable_tracker': "🛰️ Link tracking inschakelen",
        'settings_disable_tracker': "🛰️ Link tracking uitschakelen",
        'tracker_status_changed_alert': "✅ Trackingstatus bijgewerkt!",
        
        # --- Taal ---
        'lang_menu_title': "🌐 **Kies een taal**",
        'lang_uk': "🇺🇦 Українська",
        'lang_en': "🇬🇧 English",
        'lang_nl': "🇳🇱 Nederlands",
        'back_to_settings': "⬅️ Terug naar instellingen",
        'lang_changed_alert': "✅ Taal gewijzigd naar {lang_name}!",

        # --- Donaties ---
        'donate_menu_title': "💖 **Ondersteun de ontwikkeling**\n\nJouw steun in de vorm van Telegram Stars helpt de bot stabiel te draaien en te evolueren\\. Kies een bedrag dat voor jou handig is:",
        'donate_option': "{amount} ⭐",
        'donate_invoice_title': "Ondersteuning voor WH Bot Ontwikkeling",
        'donate_invoice_description': "Jouw sterren helpen de bot om zich te ontwikkelen en stabiel te werken\\. Bedankt\\!",
        'payment_successful': "🎉 Hartelijk dank voor je steun\\! Je sterren zijn ontvangen\\.",
        
        # --- Aanbod ---
        'new_listing_title': "🏠 {postcode} {city}, {street} {houseNumber}",
        'new_listing_body': "💰 Prijs: {base_price} €\n📅 Publicatiedatum: {publication_date}\n⏳ Geldig tot: {closing_date}",
        'view_listing_button': "👀 Bekijk Details",
        'no_recent_listings': "😕 Geen nieuwe advertenties in de laatste 3 dagen\\.",
        'no_active_listings': "😕 Er zijn momenteel geen actieve advertenties\\.",
        'listing_expires_in_days': "⏳ Verloopt over {days} dagen\\.",
        'listing_expires_in_hours': "⏳ Verloopt over {hours} uur\\.",
        'listing_expires_today': "🔥 Verloopt vandaag\\!",
        'sort_by_newest': "⬇️ Nieuwste",
        'sort_by_closing_date': "⏳ Bijna verlopen",
        'page_info': "Pagina {page}/{total_pages}",
        'go_to_active': "Bekijk alle actieve",
        'go_to_recent': "Bekijk recente",

        # --- Help ---
        'help_text': (
            "🤖 **WH Bot Help**\n\n"
            "Bedien de bot met de knoppen onderaan het scherm:\n\n"
            "📄 **Bekijk Aanbod** \\- toont een lijst met advertenties\\.\n\n"
            "💖 **Ondersteunen** \\- een mogelijkheid om de ontwikkelaar te steunen\\.\n\n"
            "⚙️ **Instellingen** \\- hiermee kun je meldingen, tijdzone en taal beheren\\.\n\n"
            "De bot controleert elke {interval} seconden op nieuwe advertenties\\."
        ),
    }
}