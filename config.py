#!/usr/bin/env python
import os
import sys


class Config:
    """Класс для хранения и загрузки конфигурации"""

    @staticmethod
    def load_token ():
        """Загружает токен из различных источников"""
        token = None

        try:
            # Способ 1: из python-dotenv
            try:
                from dotenv import load_dotenv
                load_dotenv ()
                token = os.getenv ('TELEGRAM_TOKEN')
                if token:
                    print (f"Загрузка токена через dotenv: Успешно")
                    return token
            except ImportError:
                print ("Модуль dotenv не найден")

            # Способ 2: из файла env.py
            try:
                sys.path.append (os.getcwd ())
                from env import TELEGRAM_TOKEN
                token = TELEGRAM_TOKEN
                print ("Загрузка токена из env.py: Успешно")
                return token
            except ImportError:
                print ("Файл env.py не найден")

            # Способ 3: напрямую из окружения
            token = os.environ.get ('TELEGRAM_TOKEN')
            if token:
                print (f"Загрузка токена из переменных окружения: Успешно")
                return token

            # Если и это не помогло, запрашиваем вручную
            token = input ("Введите ваш токен Telegram бота: ").strip ()
            return token

        except Exception as e:
            print (f"Ошибка при загрузке токена: {e}")
            token = input ("Введите ваш токен Telegram бота: ").strip ()
            return token