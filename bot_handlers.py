#!/usr/bin/env python
import asyncio
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from game_logic import GameLogic
from game_states import GameState
from telegram_ui import TelegramUI
from styles import MessageStyles
import os

class BotHandlers:
    """Класс для обработки команд и сообщений бота"""

    def __init__ (self, game_logic, ui):
        """
        Инициализация обработчиков

        Args:
            game_logic: Экземпляр класса GameLogic
            ui: Экземпляр класса TelegramUI
        """
        self.game = game_logic
        self.ui = ui
        self.styles = MessageStyles ()  # Создаем экземпляр класса MessageStyles

    async def start (self, update: Update, context: CallbackContext) -> int:
        """Начало работы с ботом"""
        user = update.effective_user

        # Сбрасываем состояние игры при запуске
        context.user_data.clear ()
        context.user_data['scene'] = 'main_menu'

        welcome_text = (
            f"Привет, {self.styles.bold (user.first_name)}! "
            f"Добро пожаловать в хоррор-новеллу {self.styles.emoji['horror']}\n\n"
            f"Вы будете играть за Алексея, пытаясь разгадать тайну заброшенного дома и своего прошлого."
        )

        # Отправляем сообщение с форматированием HTML
        await update.message.reply_text (welcome_text, parse_mode='HTML')

        # Отправляем кнопки для выбора действия
        options = ["Начать игру", "Справка", "Выйти"]
        await self.ui.send_message_with_options (update, "Выберите действие:", options)

        return GameState.MAIN_MENU

    async def begin_game (self, update: Update, context: CallbackContext) -> int:
        # Сбрасываем историю выбранных опций
        context.user_data['selected_options'] = {}

        # Показываем эффект набора текста
        await self.ui.send_typing_action (update, context)
        await asyncio.sleep (1.5)  # Небольшая задержка для реалистичности хоррора

        # Сначала отправляем изображение
        await self.ui.send_image (
            update,
            context,
            image_path='images/intro.jpg',  # Путь к изображению
        )

        # Получаем вступительный текст
        intro_raw = self.game.get_introduction ()

        # Применяем стилизацию к вступительному тексту
        intro_parts = intro_raw.split ("\n\n")

        # Форматируем нарративный текст
        narration = self.styles.format_narration (intro_parts[0])

        # Форматируем внутренний голос
        inner_voice = self.styles.format_scene_message (
            "Внутренний голос",
            intro_parts[1].replace ("Внутренний голос: ", "")
        )

        # Объединяем все части с форматированием
        intro_text = f"{narration}\n\n{inner_voice}"

        # Получаем варианты ответов для вступительной сцены
        options = self.game.get_options_for_scene ('intro')

        # Отправляем текстовое сообщение
        if update.message:
            await update.message.reply_text (intro_text, parse_mode='HTML')
        elif update.callback_query:
            await update.callback_query.message.reply_text (intro_text, parse_mode='HTML')

        # Отправляем кнопки с вариантами
        await self.ui.send_message_with_options (update, "Варианты действий:", options)

        # Сохраняем текущую сцену в контексте пользователя
        context.user_data['scene'] = 'intro'

        return GameState.IN_GAME

    async def handle_button_selection (self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        await query.answer ()  # Отвечаем на запрос, чтобы убрать "часики" на кнопке

        # Получаем текущую сцену и данные callback
        current_scene = context.user_data.get ('scene', 'main_menu')
        option_index = self.ui.get_option_index (query.data)

        print (f"Получили callback с данными: {query.data}, индекс: {option_index}, текущая сцена: {current_scene}")
        print (f"DEBUG: Инвентарь игрока: {self.game.player.inventory}")
        print (f"DEBUG: Начинаем обработку выбора. Текущая сцена: {current_scene}, индекс: {option_index}")

        # Проверяем, является ли это специальным индексом для продолжения
        if option_index == -1:
            print ("DEBUG: Это опция 'Продолжить', переходим к обработке")

            # Определяем следующую сцену в зависимости от текущей
            next_scene = self._get_next_scene_after_exhaustion (current_scene)

            # Отправляем сообщение о переходе
            transition_message = f"Алексей решает двигаться дальше, поскольку больше нечего здесь исследовать."
            formatted_message = self._apply_style_to_response (transition_message)

            await query.message.reply_text (formatted_message, parse_mode='HTML')

            # Обновляем текущую сцену
            context.user_data['scene'] = next_scene

            # Получаем варианты для новой сцены
            options = self.game.get_options_for_scene (next_scene)
            selected_options = context.user_data.get ('selected_options', {})

            # Если для новой сцены нет списка выбранных опций, создаем пустой
            if next_scene not in selected_options:
                selected_options[next_scene] = []

            # Отправляем варианты для новой сцены
            await self.ui.send_message_with_options (
                update,
                "Что будете делать?",
                options,
                disabled_options=selected_options.get (next_scene, [])
            )

            return GameState.IN_GAME

        # Специальные обработчики для главного меню
        elif current_scene == 'main_menu' or not current_scene:
            print (f"DEBUG: Обработка опции главного меню: {option_index}")
            if option_index == 0:  # "Начать игру"
                print ("DEBUG: Выбрана опция 'Начать игру'")
                return await self.begin_game (update, context)
            elif option_index == 1:  # "Справка"
                print ("DEBUG: Выбрана опция 'Справка'")
                return await self.help_command (update, context)
            elif option_index == 2:  # "Выйти"
                print ("DEBUG: Выбрана опция 'Выйти'")
                return await self.quit_command (update, context)

        # Обработка игровых опций
        else:
            print (f"DEBUG: Обработка игровой опции для сцены {current_scene}")

            # Получаем варианты ответов для текущей сцены
            options = self.game.get_options_for_scene (current_scene)
            print (f"DEBUG: Доступные опции: {options}")

            # Проверяем, что индекс опции действителен
            if option_index >= len (options):
                print (f"ERROR: Индекс опции {option_index} за пределами списка вариантов длиной {len (options)}")
                return GameState.IN_GAME

            print (f"DEBUG: Выбрана опция '{options[option_index]}'")

            # ЗДЕСЬ ДОЛЖЕН БЫТЬ ВАШ ОРИГИНАЛЬНЫЙ КОД ДЛЯ ОБРАБОТКИ ИГРОВЫХ ОПЦИЙ
            # Получаем словарь выбранных сцен из контекста пользователя
            selected_options = context.user_data.get ('selected_options', {})

            # Если для текущей сцены нет списка выбранных опций, создаем пустой
            if current_scene not in selected_options:
                selected_options[current_scene] = []

            # Обработка выбора для игровых сцен
            await self.ui.send_typing_action (update, context)
            await asyncio.sleep (2)

            # Сохраняем состояние игрока ДО обработки опции
            old_inventory = self.game.player.inventory.copy ()

            # Обрабатываем выбор пользователя
            response, next_scene = self.game.process_option_selection (current_scene, option_index)

            # Сравниваем инвентарь до и после выбора
            new_inventory = self.game.player.inventory.copy ()
            items_gained = [item for item in new_inventory if item not in old_inventory]
            if items_gained:
                print (f"DEBUG: Игрок получил новые предметы: {items_gained}")

            # Проверяем, требует ли выбранный вариант предмета, которого нет у игрока
            requires_unavailable_item = self._option_requires_unavailable_item (current_scene, option_index)

            # Добавляем текущий выбор в список выбранных для текущей сцены только если
            # он не требует недоступного предмета или добавил предмет в инвентарь
            if ((option_index not in selected_options[current_scene] and not requires_unavailable_item)
                    or items_gained):
                selected_options[current_scene].append (option_index)
                print (f"DEBUG: Добавлена опция {option_index} в список выбранных для сцены {current_scene}")
            else:
                print (
                    f"DEBUG: Опция {option_index} НЕ добавлена в список выбранных. Требует недоступный предмет: {requires_unavailable_item}")

            # Сохраняем обновленный список в контексте пользователя
            context.user_data['selected_options'] = selected_options
            print (f"DEBUG: Текущие выбранные опции: {selected_options}")

            # Применяем стилизацию к ответу
            formatted_response = self._apply_style_to_response (response)

            # Обновляем текущую сцену
            context.user_data['scene'] = next_scene

            # Если игра завершена, показываем соответствующие опции
            if next_scene == 'end':
                await query.message.reply_text (formatted_response, parse_mode='HTML')
                await self.ui.send_message_with_options (update,
                                                         "Игра окончена. Что делаем дальше?",
                                                         ["Начать заново", "Выйти"])
                context.user_data['scene'] = 'main_menu'
                return GameState.MAIN_MENU

            # Получаем варианты ответов для новой сцены
            options = self.game.get_options_for_scene (next_scene)

            # Отправляем текстовый ответ
            await query.message.reply_text (formatted_response, parse_mode='HTML')

            # Добавляем информацию об уровне страха
            if hasattr (self.game, 'player') and hasattr (self.game.player, 'fear_level'):
                fear_level_text = self.styles.format_fear_level (self.game.player.fear_level)
                await query.message.reply_text (fear_level_text, parse_mode='HTML')

            # При переходе в новую сцену используем сохраненные выбранные опции для этой сцены
            # Если сцена новая, создаем для нее пустой список
            if next_scene not in selected_options:
                selected_options[next_scene] = []

            # Распечатаем доступные опции и список скрытых опций
            print (f"DEBUG: Доступные опции для сцены {next_scene}: {options}")
            print (f"DEBUG: Скрытые опции: {selected_options.get (next_scene, [])}")

            # При отправке опций передаем список выбранных индексов для текущей сцены
            await self.ui.send_message_with_options (
                update,
                "Что будете делать?",
                options,
                disabled_options=selected_options.get (next_scene, [])
            )

            return GameState.IN_GAME

    def _get_next_scene_after_exhaustion (self, current_scene):
        """
        Определяет, в какую сцену перейти после того, как все опции
        в текущей сцене исчерпаны

        Args:
            current_scene: Текущая сцена

        Returns:
            str: Следующая сцена
        """
        # Карта переходов для разных сцен
        scene_transitions = {
            'room_with_portrait': 'corridor',
            'corridor': 'basement',
            'children_room': 'corridor',
            'basement': 'corridor',
            'library': 'corridor',
            'doctor_office': 'library'
        }

        # Если для текущей сцены определен переход, используем его
        if current_scene in scene_transitions:
            return scene_transitions[current_scene]

        # По умолчанию возвращаемся в коридор
        return 'corridor'




    def _option_requires_unavailable_item (self, scene, option_index):
        """
        Проверяет, требует ли выбранный вариант предмета, которого нет у игрока

        Args:
            scene: Текущая сцена
            option_index: Индекс выбранного варианта

        Returns:
            bool: True, если вариант требует отсутствующий предмет, иначе False
        """
        # Получаем варианты для текущей сцены
        options = self.game.get_options_for_scene (scene)
        if option_index >= len (options):
            return False

        selected_option = options[option_index].lower ()

        # Проверяем сцены и варианты, требующие предметы
        if scene == 'room_with_portrait':
            # Проверка для варианта с ящиком, который требует ключ
            if "ящик" in selected_option and not self.game.player.has_item ("ключ"):
                print (f"DEBUG: Ящик требует ключ, у игрока нет ключа")
                return True
            # Проверка для варианта с дверью, который требует ключ
            elif "дверь" in selected_option and not self.game.player.has_item ("ключ"):
                print (f"DEBUG: Дверь требует ключ, у игрока нет ключа")
                return True

        elif scene == 'library':
            # Проверка для входа в библиотеку, требующего ключ
            if not self.game.player.has_item ("ключ от библиотеки"):
                print (f"DEBUG: Библиотека требует ключ, у игрока нет ключа")
                return True

        # Добавляем отладочную информацию
        print (f"DEBUG: Опция '{selected_option}' не требует предметов или требуемые предметы есть у игрока")
        return False



    def _apply_style_to_response (self, response):
        """
        Применяет стилизацию к ответу игры

        Args:
            response: Исходный текст ответа

        Returns:
            str: Стилизованный текст
        """
        # Разделяем ответ на части (нарративный текст и диалоги)
        parts = response.split ("\n\n")
        formatted_parts = []

        for part in parts:
            if "Внутренний голос:" in part:
                # Форматируем внутренний голос
                voice_parts = part.split ("Внутренний голос:", 1)
                message_text = voice_parts[1].strip ()
                formatted_parts.append (self.styles.format_scene_message ("Внутренний голос", message_text))
            elif "Доктор Валентин:" in part:
                # Форматируем сообщение от доктора
                message_text = part.replace ("Доктор Валентин:", "").strip ()
                formatted_parts.append (self.styles.format_scene_message ("Доктор Валентин", message_text))

            elif "галлюцинац" in part.lower () or "мерещ" in part.lower () or "чудит" in part.lower ():
                # Форматируем галлюцинации особым образом
                formatted_parts.append (self.styles.format_hallucination (part))

            elif "Алексей:" in part:
                # Форматируем сообщение от Алексея
                message_text = part.replace ("Алексей:", "").strip ()
                formatted_parts.append (self.styles.format_scene_message ("Алексей", message_text))
            elif "ЗАПИСЬ ПАЦИЕНТА" in part or "ПРОТОКОЛ ЛЕЧЕНИЯ" in part:
                # Форматируем медицинские записи как код
                formatted_parts.append (self.styles.code (part))
            elif "ХОРОШАЯ КОНЦОВКА" in part:
                # Форматируем текст хорошей концовки
                formatted_parts.append (self.styles.format_ending ("good", part))
            elif "ПЛОХАЯ КОНЦОВКА" in part:
                # Форматируем текст плохой концовки
                formatted_parts.append (self.styles.format_ending ("bad", part))
            elif "СЕКРЕТНАЯ КОНЦОВКА" in part:
                # Форматируем текст секретной концовки
                formatted_parts.append (self.styles.format_ending ("secret", part))
            elif "НЕЙТРАЛЬНАЯ КОНЦОВКА" in part:
                # Форматируем текст нейтральной концовки
                formatted_parts.append (self.styles.format_ending ("neutral", part))
            elif part.startswith ("'") and part.endswith ("'") and len (part) > 10:
                # Форматируем цитаты и записи как выделенный текст
                formatted_parts.append (self.styles.format_horror_effect (part.strip ("'")))
            else:
                # Остальной текст - это нарратив
                formatted_parts.append (self.styles.format_narration (part))

        # Объединяем форматированные части
        return "\n\n".join (formatted_parts)

    async def handle_message (self, update: Update, context: CallbackContext) -> int:
        """Обработка текстовых сообщений (устаревший метод, оставлен для совместимости)"""
        user_message = update.message.text
        current_scene = context.user_data.get ('scene', 'intro')

        # Показываем эффект набора текста
        await self.ui.send_typing_action (update, context)
        await asyncio.sleep (2)  # Задержка для реалистичности хоррора

        # Получаем ответ и следующую сцену
        response, next_scene = self.game.process_input (current_scene, user_message)

        # Применяем стилизацию к ответу
        formatted_response = self._apply_style_to_response (response)

        # Получаем словарь выбранных сцен из контекста пользователя
        selected_options = context.user_data.get ('selected_options', {})

        # Если для текущей сцены нет списка выбранных опций, создаем пустой
        if next_scene not in selected_options:
            selected_options[next_scene] = []

        # Обновляем текущую сцену
        context.user_data['scene'] = next_scene

        # Отправляем ответ
        await update.message.reply_text (formatted_response, parse_mode='HTML')

        # Добавляем информацию об уровне страха, если персонаж в игре
        if hasattr (self.game, 'player') and hasattr (self.game.player, 'fear_level'):
            fear_level_text = self.styles.format_fear_level (self.game.player.fear_level)
            await update.message.reply_text (fear_level_text, parse_mode='HTML')

        # Если игра закончилась
        if next_scene == 'end':
            options = ["Начать заново", "Выйти"]
            await self.ui.send_message_with_options (update, "Игра окончена. Что делаем дальше?", options)
            return GameState.MAIN_MENU

        # Для всех остальных сцен показываем варианты ответов
        options = self.game.get_options_for_scene (next_scene)
        await self.ui.send_message_with_options (
            update,
            "Что будете делать?",
            options,
            disabled_options=selected_options.get (next_scene, [])
        )

        return GameState.IN_GAME

    async def help_command (self, update: Update, context: CallbackContext) -> int:
        """Отправка сообщения с помощью"""
        help_text = (
            f"{self.styles.emoji['game']} {self.styles.bold ('Как играть:')}\n\n"
            f"1. Нажмите кнопку {self.styles.bold ('Начать игру')}\n"
            f"2. Читайте происходящие события и выбирайте варианты действий\n"
            f"3. Ваши решения влияют на развитие сюжета и уровень страха персонажа\n"
            f"4. Исследуйте дом, найдите скрытые предметы и раскройте тайну своего прошлого\n\n"
            f"{self.styles.emoji['info']} {self.styles.bold ('Команды:')}\n"
            f"/start - Перезапустить бота\n"
            f"/begin - Начать новую игру\n"
            f"/help - Показать эту справку\n"
            f"/quit - Выйти из игры"
        )

        # Отправляем сообщение с форматированием HTML
        if update.message:
            await update.message.reply_text (help_text, parse_mode='HTML')
        elif update.callback_query:
            await update.callback_query.message.reply_text (help_text, parse_mode='HTML')

        # Показываем кнопки для возврата
        options = ["Начать игру", "Выйти"]
        await self.ui.send_message_with_options (update, "Что дальше?", options)

        return GameState.MAIN_MENU

    async def quit_command (self, update: Update, context: CallbackContext) -> int:
        """Выход из игры"""
        message = (
            f"Спасибо за игру! {self.styles.emoji['skull']} "
            f"Чтобы снова погрузиться в кошмар, введите /start."
        )

        if update.message:
            await update.message.reply_text (message, parse_mode='HTML')
        elif update.callback_query:
            await update.callback_query.message.reply_text (message, parse_mode='HTML')

        return ConversationHandler.END