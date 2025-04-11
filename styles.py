#!/usr/bin/env python
"""
Модуль для стилизации сообщений и визуальных элементов в Telegram.
Здесь определены стили сообщений, эмодзи и форматирование текста.
"""


class MessageStyles:
    """Стили и форматирование сообщений"""

    # Эмодзи для разных ситуаций
    EMOJI = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': '📝',
        'question': '❓',
        'ghost': '👻',
        'skull': '💀',
        'horror': '😱',
        'blood': '🩸',
        'key': '🔑',
        'door': '🚪',
        'house': '🏚️',
        'book': '📕',
        'light': '🔦',
        'dark': '🌑',
        'fire': '🔥',
        'scream': '😱',
        'eyes': '👁️',
        'shadow': '👤',
        'whisper': '🤫',
        'memory': '💭',
        'photograph': '📷',
        'room': '🛏️',
        'basement': '🪜',
        'library': '📚',
        'children': '🧸',
        'medical': '💉',
        'clock': '🕐',
        'dream': '💤',
        'fog': '🌫️',
        'lock': '🔒',
        'unlock': '🔓',
        'smile': '😊',
        'sad': '😔',
        'game': '🎮',
        'options': '🔢',
        'hallucination': '🌀',
        'insanity': '🤪',
        'reality': '🌗',
    }

    def __init__ (self):
        """Инициализация объекта стилей"""
        # Создаем атрибут emoji для обращения через self.emoji
        self.emoji = self.EMOJI

    def bold (self, text):
        """Жирный текст"""
        return f"<b>{text}</b>"

    def italic (self, text):
        """Курсивный текст"""
        return f"<i>{text}</i>"

    def code (self, text):
        """Моноширинный текст (код)"""
        return f"<code>{text}</code>"

    def underline (self, text):
        """Подчеркнутый текст"""
        return f"<u>{text}</u>"

    def strikethrough (self, text):
        """Зачеркнутый текст"""
        return f"<s>{text}</s>"

    def link (self, text, url):
        """Текст со ссылкой"""
        return f'<a href="{url}">{text}</a>'

    def horror_title (self, text):
        """Форматирование заголовка в стиле хоррора"""
        return f"{self.emoji['skull']} {self.bold (text.upper ())} {self.emoji['skull']}"

    def format_scene_message (self, character_name, message_text):
        """
        Форматирует сообщение от персонажа

        Args:
            character_name: Имя персонажа
            message_text: Текст сообщения

        Returns:
            str: Отформатированное сообщение
        """
        emoji = ''
        if character_name == "Доктор Валентин":
            emoji = self.emoji['medical']
        elif character_name == "Призрак":
            emoji = self.emoji['ghost']
        elif "воспоминание" in character_name.lower ():
            emoji = self.emoji['memory']
        elif "голос" in character_name.lower ():
            emoji = self.emoji['whisper']

        return f"{self.bold (character_name)}{emoji}: {message_text}"

    def format_narration (self, text):
        """
        Форматирует текст повествования

        Args:
            text: Текст повествования

        Returns:
            str: Отформатированный текст
        """
        return f"{self.italic (text)}"

    def format_horror_effect (self, text):
        """
        Форматирует текст с эффектом хоррора - обрывочные фразы, шепот и т.д.

        Args:
            text: Исходный текст

        Returns:
            str: Текст с эффектом хоррора
        """
        return f"{self.emoji['whisper']} {self.italic (text)} {self.emoji['whisper']}"

    def format_options_header (self):
        """
        Возвращает заголовок для списка вариантов ответа

        Returns:
            str: Отформатированный заголовок
        """
        return f"\n\n{self.emoji['options']} {self.bold ('Выберите действие:')}"

    def format_options (self, options):
        """
        Форматирует список вариантов ответа

        Args:
            options: Список вариантов

        Returns:
            str: Отформатированный список
        """
        header = self.format_options_header ()
        options_text = ""

        for i, option in enumerate (options, 1):
            options_text += f"\n{i}. {option}"

        return f"{header}{options_text}"

    def format_ending (self, ending_type, text):
        """
        Форматирует текст концовки

        Args:
            ending_type: Тип концовки ('good', 'neutral', 'bad', 'secret')
            text: Текст концовки

        Returns:
            str: Отформатированный текст
        """
        emoji = self.emoji['smile']  # Хорошая концовка
        if ending_type == 'neutral':
            emoji = self.emoji['memory']
        elif ending_type == 'bad':
            emoji = self.emoji['scream']
        elif ending_type == 'secret':
            emoji = self.emoji['unlock']

        return f"{self.bold (f'КОНЦОВКА {emoji}')}\n\n{text}"

    def format_location (self, location_name):
        """
        Форматирует название локации

        Args:
            location_name: Название локации

        Returns:
            str: Отформатированное название
        """
        location_lower = location_name.lower ()
        emoji = ''

        if 'комната' in location_lower:
            emoji = self.emoji['room']
        elif 'коридор' in location_lower:
            emoji = self.emoji['door']
        elif 'подвал' in location_lower:
            emoji = self.emoji['basement']
        elif 'библиотека' in location_lower:
            emoji = self.emoji['library']
        elif 'детская' in location_lower:
            emoji = self.emoji['children']
        elif 'кабинет' in location_lower:
            emoji = self.emoji['medical']
        else:
            emoji = self.emoji['house']

        return f"{emoji} {self.bold (location_name.upper ())}"

    def format_fear_level (self, level):
        """
        Форматирует уровень страха

        Args:
            level: Уровень страха (0-100)

        Returns:
            str: Отформатированное представление уровня страха
        """
        if level < 20:
            return f"{self.emoji['smile']} Уровень страха: низкий"
        elif level < 50:
            return f"{self.emoji['warning']} Уровень страха: средний"
        elif level < 80:
            return f"{self.emoji['horror']} Уровень страха: высокий"
        else:
            return f"{self.emoji['scream']} Уровень страха: критический!"

    def format_hallucination (self, text):
        """
        Форматирует текст галлюцинации, чтобы он отделялся от основного текста

        Args:
            text: Текст галлюцинации

        Returns:
            str: Отформатированный текст
        """
        # Используем HTML-форматирование для создания блока с галлюцинацией
        # Добавляем эмодзи в начало и конец, используем курсив и зачеркивание
        return f"<i>{self.emoji['hallucination']} <s>{text}</s> {self.emoji['hallucination']}</i>"