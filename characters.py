#!/usr/bin/env python

class Character:
    """Базовый класс для всех персонажей"""

    def __init__ (self, name, age, description):
        self.name = name
        self.age = age
        self.description = description
        self.relationships = {}

    def add_relationship (self, character_name, relationship_type, level=0):
        """Добавление отношений с другим персонажем"""
        self.relationships[character_name] = {
            'type': relationship_type,  # друг, враг, память и т.д.
            'level': level  # от -100 до 100
        }

    def get_relationship (self, character_name):
        """Получение типа и уровня отношений с персонажем"""
        if character_name in self.relationships:
            return self.relationships[character_name]
        return {'type': 'незнакомец', 'level': 0}

    def update_relationship (self, character_name, delta):
        """Изменение уровня отношений"""
        if character_name in self.relationships:
            self.relationships[character_name]['level'] += delta
            # Ограничение значений от -100 до 100
            self.relationships[character_name]['level'] = max (-100,
                                                               min (100, self.relationships[character_name]['level']))


class Player (Character):
    """Класс игрока (Алексей)"""

    def __init__ (self):
        super ().__init__ (
            name="Алексей",
            age=35,
            description="Мужчина, страдающий от потери памяти и чувства вины."
        )
        self.inventory = []
        self.story_flags = set ()
        self.fear_level = 0  # Уровень страха от 0 до 100

    def add_to_inventory (self, item):
        """Добавление предмета в инвентарь"""
        self.inventory.append (item)

    def remove_from_inventory (self, item):
        """Удаление предмета из инвентаря"""
        if item in self.inventory:
            self.inventory.remove (item)
            return True
        return False

    def has_item (self, item):
        """Проверка наличия предмета в инвентаре"""
        return item in self.inventory

    def add_flag (self, flag):
        """Добавление флага сюжета"""
        self.story_flags.add (flag)

    def has_flag (self, flag):
        """Проверка наличия флага сюжета"""
        return flag in self.story_flags

    def increase_fear (self, amount):
        """Увеличение уровня страха"""
        self.fear_level += amount
        # Ограничиваем максимальный уровень страха
        self.fear_level = min (100, self.fear_level)

    def decrease_fear (self, amount):
        """Уменьшение уровня страха"""
        self.fear_level -= amount
        # Уровень страха не может быть отрицательным
        self.fear_level = max (0, self.fear_level)


class DoctorValentin (Character):
    """Класс доктора Валентина - антагониста"""

    def __init__ (self):
        super ().__init__ (
            name="Доктор Валентин",
            age=60,
            description="Психиатр, проводивший экспериментальные методы лечения."
        )
        self.responses = {
            'default': [
                "Алексей, ваши воспоминания все еще подавлены. Доверьтесь процессу.",
                "Интересно, что вызвало такую реакцию...",
                "Продолжайте исследовать дом, и память вернется.",
            ],
            'threatening': [
                "Вы не должны заходить так далеко. Некоторые двери лучше держать закрытыми.",
                "Алексей, вы не готовы к правде. Уходите, пока можете.",
                "То, что вы ищете, может уничтожить вас. Не все воспоминания стоит возвращать.",
            ],
            'manipulative': [
                "Вы сами пришли ко мне за помощью, Алексей. Помните это.",
                "Разве не вы хотели забыть? Теперь вы должны принять последствия.",
                "Ваше чувство вины разрушило вас. Я лишь пытался помочь.",
            ],
        }

    def get_response (self, mood='default', idx=0):
        """Получение ответа определенного настроения"""
        if mood not in self.responses:
            mood = 'default'

        # Если индекс за пределами списка, берем случайный ответ
        if idx >= len (self.responses[mood]):
            import random
            return random.choice (self.responses[mood])

        return self.responses[mood][idx]


class Ghost (Character):
    """Класс для призрачных персонажей"""

    def __init__ (self, name, age, description, ghost_type='family'):
        super ().__init__ (name, age, description)
        self.ghost_type = ghost_type  # family, victim, враждебный

        # Тип сообщений от призрака
        self.whispers = {
            'family': [
                "Помнишь нас?",
                "Почему ты не спас нас?",
                "Мы скучаем по тебе...",
                "Ты обещал всегда быть рядом...",
            ],
            'cryptic': [
                "Ключ в твоих воспоминаниях...",
                "Следуй за шепотом прошлого...",
                "Некоторые двери должны оставаться закрытыми...",
                "Дом знает твои секреты...",
            ],
            'helping': [
                "Не верь ему...",
                "Ищи фотографии...",
                "Правда в библиотеке...",
                "Ты не виноват...",
            ]
        }

    def get_whisper (self, mood='cryptic', idx=0):
        """Получение шепота определенного типа"""
        if mood not in self.whispers:
            mood = 'cryptic'

        # Если индекс за пределами списка, берем случайный ответ
        if idx >= len (self.whispers[mood]):
            import random
            return random.choice (self.whispers[mood])

        return self.whispers[mood][idx]