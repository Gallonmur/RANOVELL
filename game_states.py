#!/usr/bin/env python
from enum import Enum, auto

class GameState(Enum):
    """Состояния игры для ConversationHandler"""
    MAIN_MENU = auto()
    IN_GAME = auto()