#!/usr/bin/env python
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler
)

from config import Config
from game_logic import GameLogic
from game_states import GameState
from telegram_ui import TelegramUI
from bot_handlers import BotHandlers

# Настройка логирования
logging.basicConfig (
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger (__name__)


def main () -> None:
    """Запуск бота"""
    print ("Инициализация бота...")

    # Загрузка токена
    TOKEN = Config.load_token ()
    if not TOKEN:
        print ("ОШИБКА: Токен не найден или пустой!")
        exit (1)
    else:
        # Показываем только первые и последние 5 символов токена для безопасности
        print (f"Токен загружен: {TOKEN[:5]}...{TOKEN[-5:]}")

    # Инициализация компонентов
    game = GameLogic ()
    ui = TelegramUI ()
    handlers = BotHandlers (game, ui)

    # Создаем приложение
    application = Application.builder ().token (TOKEN).build ()

    # Создаем обработчик разговора
    conv_handler = ConversationHandler (
        entry_points=[CommandHandler ('start', handlers.start)],
        states={
            GameState.MAIN_MENU: [
                CommandHandler ('begin', handlers.begin_game),
                CommandHandler ('help', handlers.help_command),
                CommandHandler ('quit', handlers.quit_command),
                CallbackQueryHandler (handlers.handle_button_selection),
            ],
            GameState.IN_GAME: [
                MessageHandler (filters.TEXT & ~filters.COMMAND, handlers.handle_message),
                CommandHandler ('help', handlers.help_command),
                CommandHandler ('quit', handlers.quit_command),
                CallbackQueryHandler (handlers.handle_button_selection),
            ],
        },
        fallbacks=[CommandHandler ('quit', handlers.quit_command)],
    )

    # Добавляем обработчик разговора
    application.add_handler (conv_handler)

    # Запускаем бота
    print ("Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling ()


if __name__ == '__main__':
    main ()