# Инициализация модуля Bullet Hell
import renpy.exports as renpy

# Автоматический импорт всех модулей при инициализации
from .config import *
from .displayables import *
from .player import *
from .assistant import *
from .attacks import *
from .game import *

# Инициализация глобальных переменных
sizes = None