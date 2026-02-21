# game/bullet_hell/config.rpy
init python:
    # Конфигурация Bullet Hell игры

    # Относительные размеры (проценты от экрана)
    SCREEN_PADDING = 0.02
    GAME_ZONE_WIDTH_RATIO = 0.60
    SIDE_PANEL_WIDTH_RATIO = 0.20
    TOP_PANEL_HEIGHT_RATIO = 0.10
    BOTTOM_PANEL_HEIGHT_RATIO = 0.06

    # Время игры в секундах
    GAME_DURATION = 120.0  # 2 минуты
    CRITICAL_TIME = 46
    GAME_START_DELAY = 3.0  # Задержка перед началом атак

    # Типы атак (ДОБАВИЛИ МЕДЛЕННЫЕ ПУЛИ)
    ATTACK_SLOW_BULLET = 0   # Медленные пули размером с игрока (пассивные)
    ATTACK_ARROWS_1 = 1      # 3 параллельные стрелы
    ATTACK_ARROWS_2 = 2      # 5 стрел по дуге
    ATTACK_SPHERE_BURST = 3  # Шар + взрыв

    # Цвета
    COLORS = {
        "game_zone": "#333333",
        "player": "#ff0000",
        "assistant_base": "#87CEEB",
        "assistant_active": "#00BFFF",
        "bullet_fill": "#FFFFFF",
        "bullet_outline": "#000000",
        "sphere_main": "#FFFFFF",  # БЕЛЫЙ цвет для основного шара
        "shield": "#FFD700",
        "time_slow": "#87CEEB",
        "ui_background": "#222222DD",
        "ui_text": "#FFFFFF",
        "life_full": "#ff0000",
        "life_empty": "#444444",
        "progress_background": "#333333DD",
        "progress_marker": "#FFFF00",
        "progress_critical": "#FF0000",
    }

    class BulletHellConfig:
        def __init__(self):
            self.game_duration = GAME_DURATION
            self.critical_time = CRITICAL_TIME
            self.game_start_delay = GAME_START_DELAY
            self.colors = COLORS.copy()
            self.background_image = "images/space.jpg"
            self.game_zone_color = COLORS["game_zone"]

            # Параметры игрока
            self.player_size_ratio = 0.025
            self.player_speed = (400, 400)
            self.player_max_lives = 3
            self.player_invincible_time = 1.2
            self.dash_cooldown = 0.4
            self.dash_duration = 0.15
            self.dash_distance_multiplier = 6

            # Параметры помощника
            self.assistant_size_ratio = 0.04
            self.ability_cooldowns = [15.0, 15.0, 15.0]
            self.ability_durations = [3.0, 3.0, 3.0]
            self.min_time_between_abilities = 3.0

            # Параметры пуль
            self.arrow_length = 0.035
            self.arrow_width = 0.015
            self.sphere_radius_ratio = 0.025
            self.mini_sphere_ratio = 0.012
            self.bullet_max_lifetime = 10.0

            # Параметры медленных пуль (тип 0)
            self.slow_bullet_size_ratio = 0.025  # Размер как у игрока
            self.slow_bullet_speed_multiplier = 0.8  # 20% медленнее стрел типа 2

            # Расстояние между пулями в атаках - УМЕНЬШЕНО
            self.arrows_spacing = 0.12  # Было 0.2 - УМЕНЬШИЛИ

            # Базовые интервалы атак - ИЗМЕНЕНЫ
            self.base_attack_interval = 2.0  # Было 3.0 - УМЕНЬШИЛИ
            self.min_attack_interval = 0.5   # Было 1.0 - УМЕНЬШИЛИ

            # Время уменьшения интервала до минимума (90 секунд)
            self.interval_decrease_time = 90.0

            # Пассивные пули (тип 0) - настройки частоты
            self.slow_bullet_start_rate = 1.0    # 1 пуля в секунду в начале
            self.slow_bullet_end_rate = 5.0      # 5 пуль в секунду к 1:30
            self.slow_bullet_last_spawn = -10    # Время последнего спавна

            # Критический режим
            self.critical_attack_repeat_delay = 1.0

            # Скорости снарядов
            self.arrow_speed = 400
            self.sphere_speed = 300
            self.mini_sphere_speed = 350
            self.slow_bullet_speed = 320  # 400 * 0.8 = 320 (на 20% медленнее стрел)

            # Другие параметры
            self.time_slow_factor = 0.4
            self.time_slow_radius_multiplier = 10
            self.shield_size_multiplier = 1.5
            self.sphere_explosion_delay = 0.8

    # Расчет абсолютных размеров
    def calculate_sizes():
        screen_width = renpy.config.screen_width
        screen_height = renpy.config.screen_height

        return {
            "screen_width": screen_width,
            "screen_height": screen_height,
            "padding": int(screen_width * SCREEN_PADDING),
            "side_panel_width": int(screen_width * SIDE_PANEL_WIDTH_RATIO),
            "top_panel_height": int(screen_height * TOP_PANEL_HEIGHT_RATIO),
            "bottom_panel_height": int(screen_height * BOTTOM_PANEL_HEIGHT_RATIO),
            "game_zone_width": int(screen_width * GAME_ZONE_WIDTH_RATIO),
        }

    # Глобальные переменные с размерами
    sizes = None