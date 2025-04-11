#!/usr/bin/env python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext


class TelegramUI:
    """Класс для управления пользовательским интерфейсом Telegram"""

    def __init__ (self):
        """Инициализация пользовательского интерфейса"""
        # Словарь для хранения кэшированных клавиатур
        self.cached_keyboards = {}

    async def send_message_with_options (self, update: Update, text: str, options: list,
                                         options_per_row: int = 3,
                                         disabled_options: list = None):
        """
        Отправляет сообщение с вариантами ответа и цифровыми кнопками.
        Выбранные варианты полностью удаляются.

        Args:
            update: Объект Update из Telegram
            text: Текст сообщения
            options: Список вариантов ответа
            options_per_row: Количество кнопок в одном ряду
            disabled_options: Список индексов опций, которые нужно удалить
        """
        # Если список disabled_options не передан, создаем пустой
        if disabled_options is None:
            disabled_options = []

        print (f"DEBUG: Все опции: {options}")
        print (f"DEBUG: Отключенные опции: {disabled_options}")

        # Проверяем - не все ли опции отключены
        all_disabled = len (disabled_options) >= len (options)

        # Если все опции отключены, добавляем вариант "Продолжить"
        if all_disabled:
            print ("DEBUG: Все опции отключены, добавляем вариант 'Продолжить'")
            filtered_options = ["Продолжить"]
            option_map = {0: -1}  # Используем специальный индекс -1 для "Продолжить"
        else:
            # Фильтруем опции, удаляя выбранные
            filtered_options = [
                option for i, option in enumerate (options)
                if i not in disabled_options
            ]

            # Создаем карту соответствия оригинальных индексов и новых
            option_map = {
                new_idx: orig_idx
                for new_idx, orig_idx in enumerate ([
                    i for i in range (len (options))
                    if i not in disabled_options
                ])
            }

        print (f"DEBUG: Отфильтрованные опции: {filtered_options}")
        print (f"DEBUG: Карта индексов: {option_map}")

        # Создаем текст с вариантами ответов
        options_text = "\n\nВыберите ответ:\n"
        for i, option in enumerate (filtered_options, 1):
            options_text += f"{i}. {option}\n"

        # Полный текст сообщения с вариантами
        full_text = f"{text}{options_text}"

        # Создаем кнопки с цифрами и соответствующими callback_data
        keyboard = []
        row = []

        for i in range (len (filtered_options)):
            # Используем отображение, чтобы сохранить исходный индекс опции
            original_index = option_map[i]

            row.append (InlineKeyboardButton (
                str (i + 1),  # Нумерация для пользователя начинается с 1
                callback_data=f"option_{original_index}"  # Оригинальный индекс для обработки
            ))

            # Если заполнили ряд или это последняя кнопка
            if (i + 1) % options_per_row == 0 or i == len (filtered_options) - 1:
                keyboard.append (row)
                row = []

        reply_markup = InlineKeyboardMarkup (keyboard)

        # Определяем, откуда отправлять сообщение
        if update.message:
            await update.message.reply_text (full_text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.reply_text (full_text, reply_markup=reply_markup)
        else:
            print ("Ошибка: Не удалось определить источник сообщения")

    def get_quick_reply_keyboard (self, options: list, one_time: bool = False):
        """
        Создает клавиатуру быстрых ответов

        Args:
            options: Список вариантов ответа
            one_time: Скрыть клавиатуру после использования

        Returns:
            ReplyKeyboardMarkup: Объект клавиатуры
        """
        keyboard = [[KeyboardButton (option)] for option in options]
        return ReplyKeyboardMarkup (
            keyboard,
            one_time_keyboard=one_time,
            resize_keyboard=True
        )

    # В методе get_option_index в классе TelegramUI
    def get_option_index (self, callback_data: str) -> int:
        """
        Извлекает индекс выбранного варианта из callback_data
        """
        print (f"DEBUG: Получены callback данные: '{callback_data}'")
        if callback_data.startswith ("option_"):
            try:
                index = int (callback_data.replace ("option_", ""))
                print (f"DEBUG: Извлечен индекс: {index}")
                return index
            except ValueError:
                print (f"DEBUG: Ошибка при преобразовании индекса")
                return -1
        print (f"DEBUG: Неизвестный формат callback данных")
        return -1

    async def send_image (self, update: Update, context: CallbackContext, image_path: str, caption: str = None):
        """
        Отправляет изображение

        Args:
            update: Объект Update из Telegram
            context: Контекст обработчика
            image_path: Путь к изображению
            caption: Подпись к изображению
        """
        try:
            chat_id = update.effective_chat.id
            with open (image_path, 'rb') as image:
                await context.bot.send_photo (
                    chat_id=chat_id,
                    photo=image,
                    caption=caption
                )
        except Exception as e:
            print (f"Ошибка отправки изображения: {e}")
            # В случае ошибки отправляем только текст
            if caption:
                if update.message:
                    await update.message.reply_text (caption)
                elif update.callback_query:
                    await update.callback_query.message.reply_text (caption)

    async def send_typing_action (self, update: Update, context: CallbackContext):
        """
        Показывает индикатор 'печатает...'

        Args:
            update: Объект Update из Telegram
            context: Контекст обработчика
        """
        await context.bot.send_chat_action (
            chat_id=update.effective_chat.id,
            action="typing"
        )