#!/usr/bin/env python
import random


class HallucinationSystem:
    """Система для добавления галлюцинаций и искажений реальности при высоком уровне страха"""

    def __init__ (self, game_logic):
        """
        Инициализация системы галлюцинаций

        Args:
            game_logic: Экземпляр класса GameLogic, для доступа к игре
        """
        self.game = game_logic

        # Галлюцинации для разных сцен
        self.hallucinations = {
            'common': [  # Общие галлюцинации для всех сцен
                "Краем глаза Алексей замечает движущуюся тень, но когда оборачивается - никого нет.",
                "На мгновение кажется, что все предметы в комнате слегка вибрируют.",
                "Алексею чудится шепот за спиной, но слов не разобрать.",
                "На стене мелькает темный силуэт, исчезая, когда Алексей смотрит прямо на него.",
                "Собственное отражение в тусклом стекле кажется искаженным, будто это кто-то другой."
            ],
            'room_with_portrait': [
                "Глаза на портрете, кажется, следят за каждым движением Алексея.",
                "На секунду портрет меняется, и женщина на нем начинает плакать кровавыми слезами.",
                "Алексей слышит тихий плач, исходящий от портрета."
            ],
            'corridor': [
                "Коридор на мгновение кажется бесконечно длинным, стены уходят вдаль.",
                "Двери по бокам коридора начинают беззвучно открываться и закрываться.",
                "Под ногами проступают темные пятна, похожие на кровь, но через секунду исчезают."
            ],
            'children_room': [
                "Игрушки на полке поворачивают головы, следя за Алексеем.",
                "Из шкатулки на мгновение доносится детский смех, сменяющийся плачем.",
                "Алексей видит маленькие следы босых ног, ведущие в стену и исчезающие."
            ],
            'basement': [
                "В темноте подвала мелькают красные глаза, десятки пар.",
                "Стены подвала, кажется, пульсируют, словно живые.",
                "Алексей чувствует на шее чье-то дыхание, но обернувшись, никого не видит."
            ],
            'library': [
                "Буквы в книгах шевелятся и меняют местами, складываясь в пугающие послания.",
                "С полок падают книги, раскрываясь на страницах с рисунками ритуальных убийств.",
                "Алексей слышит шепот, доносящийся из-за книжных полок."
            ],
            'doctor_office': [
                "Медицинские инструменты на столе кажутся покрытыми свежей кровью.",
                "Силуэт доктора мелькает в отражениях, хотя в комнате никого нет.",
                "Кресло в центре комнаты поворачивается само по себе, словно в нем кто-то сидит."
            ]
        }

        # Ложные варианты действий для разных сцен
        self.false_options = {
            'common': [
                "Прислушаться к шепоту",
                "Проверить тень в углу",
                "Закрыть глаза и сосчитать до десяти",
                "Позвать на помощь"
            ],
            'room_with_portrait': [
                "Сорвать портрет со стены",
                "Заговорить с женщиной на портрете"
            ],
            'corridor': [
                "Бежать до конца коридора",
                "Спрятаться в тени"
            ],
            'children_room': [
                "Собрать игрушки в кучу",
                "Поискать ребенка под кроватью"
            ],
            'basement': [
                "Погасить свет",
                "Закрыть глаза и прислушаться"
            ],
            'library': [
                "Сжечь пугающие книги",
                "Прочитать заклинание с открытой страницы"
            ],
            'doctor_office': [
                "Разбить зеркало",
                "Попытаться связаться с доктором"
            ]
        }

    def get_hallucination (self, scene):
        """
        Возвращает случайную галлюцинацию для заданной сцены

        Args:
            scene: Текущая сцена

        Returns:
            str: Текст галлюцинации
        """
        # Комбинируем общие галлюцинации и специфичные для сцены
        available_hallucinations = self.hallucinations.get ('common', [])
        scene_specific = self.hallucinations.get (scene, [])
        available_hallucinations.extend (scene_specific)

        # Если для сцены нет галлюцинаций, возвращаем пустую строку
        if not available_hallucinations:
            return ""

        return random.choice (available_hallucinations)

    def get_false_option (self, scene):
        """
        Возвращает случайный ложный вариант действия для заданной сцены

        Args:
            scene: Текущая сцена

        Returns:
            str: Текст ложного варианта
        """
        # Комбинируем общие варианты и специфичные для сцены
        available_options = self.false_options.get ('common', [])
        scene_specific = self.false_options.get (scene, [])
        available_options.extend (scene_specific)

        # Если для сцены нет вариантов, возвращаем None
        if not available_options:
            return None

        return random.choice (available_options)

    def apply_hallucination_effects (self, response, scene):
        """
        Применяет эффекты галлюцинаций к ответу игры

        Args:
            response: Исходный текст ответа
            scene: Текущая сцена

        Returns:
            str: Измененный текст с галлюцинациями
        """
        # Получаем уровень страха игрока
        fear_level = self.game.player.fear_level


        # Если уровень страха низкий, ничего не меняем
        if fear_level < 30:
            return response

        # Определяем вероятность галлюцинации в зависимости от уровня страха
        hallucination_chance = (fear_level - 50) / 100.0

        # Чем выше уровень страха, тем больше галлюцинаций
        num_hallucinations = 0
        if fear_level >= 80:
            num_hallucinations = random.randint (1, 2)
        elif fear_level >= 50:
            if random.random () < hallucination_chance:
                num_hallucinations = 1

        # Если нет галлюцинаций, возвращаем исходный текст
        if num_hallucinations == 0:
            return response

        # Разделяем ответ на абзацы
        paragraphs = response.split ("\n\n")

        # Добавляем галлюцинации
        for _ in range (num_hallucinations):
            hallucination_text = self.get_hallucination (scene)
            if hallucination_text:
                # Добавляем галлюцинацию как новый абзац в случайное место
                insert_pos = random.randint (0, len (paragraphs))
                paragraphs.insert (insert_pos, hallucination_text)

        # Объединяем абзацы обратно
        return "\n\n".join (paragraphs)

    def add_false_options (self, options, scene):
        """
        Добавляет ложные варианты действий в список опций

        Args:
            options: Список оригинальных вариантов действий
            scene: Текущая сцена

        Returns:
            list: Обновленный список вариантов
        """
        # Получаем уровень страха игрока
        fear_level = self.game.player.fear_level


        # Если уровень страха низкий, ничего не меняем
        if fear_level < 30:
            return options

        # Определяем вероятность появления ложного варианта
        false_option_chance = (fear_level - 70) / 100.0

        # Добавляем ложный вариант только при высоком уровне страха и по вероятности
        if random.random () < false_option_chance:
            false_option = self.get_false_option (scene)
            if false_option and false_option not in options:
                # Добавляем ложный вариант в случайную позицию
                position = random.randint (0, len (options))
                options.insert (position, false_option)

        return options