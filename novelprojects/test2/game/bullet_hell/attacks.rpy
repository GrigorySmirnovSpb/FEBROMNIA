# game/bullet_hell/attacks.rpy
init python:
    import pygame as pg
    import random
    import math

    class AttackManager:
        def __init__(self, config, game_instance):
            self.config = config
            self.game = game_instance

            # Время последней атаки
            self.last_attack_time = -10

            # Список доступных атак (без медленных пуль)
            self.available_attacks = [
                ATTACK_ARROWS_1,
                ATTACK_ARROWS_2,
                ATTACK_SPHERE_BURST
            ]

            # Случайный порядок атак
            self.attack_queue = []
            self.generate_attack_queue()

            # Флаг для повтора атаки в критическом режиме
            self.repeat_attack = False
            self.repeat_delay = 0
            self.last_attack_type = None

            # Время последнего спавна медленных пуль
            self.last_slow_bullet_time = -10

        def generate_attack_queue(self):
            """Генерирует случайную очередь атак"""
            self.attack_queue = self.available_attacks.copy()
            random.shuffle(self.attack_queue)

        def get_next_attack(self):
            """Получает следующую атаку из очереди"""
            if not self.attack_queue:
                self.generate_attack_queue()
            return self.attack_queue.pop(0)

        def get_current_attack_interval(self, current_time):
            """Рассчитывает текущий интервал между атаками"""
            # Учитываем начальную задержку
            if current_time < self.config.game_start_delay:
                return 9999.0

            effective_time = current_time - self.config.game_start_delay

            if effective_time <= 0:
                return self.config.base_attack_interval

            # Линейное уменьшение интервала
            progress = min(1.0, effective_time / self.config.interval_decrease_time)

            current_interval = (
                self.config.base_attack_interval -
                (self.config.base_attack_interval - self.config.min_attack_interval) * progress
            )

            # В критическом режиме уменьшаем интервал еще на 30%
            if effective_time > self.config.critical_time:
                current_interval *= 0.7

            return max(self.config.min_attack_interval, current_interval)

        def get_current_slow_bullet_interval(self, current_time):
            """Рассчитывает текущий интервал для медленных пуль"""
            # Учитываем начальную задержку
            if current_time < self.config.game_start_delay:
                return 9999.0

            effective_time = current_time - self.config.game_start_delay

            if effective_time <= 0:
                return 1.0 / self.config.slow_bullet_start_rate

            # Линейное увеличение частоты
            progress = min(1.0, effective_time / self.config.interval_decrease_time)

            # Интерполируем частоту от start_rate до end_rate
            current_rate = (
                self.config.slow_bullet_start_rate +
                (self.config.slow_bullet_end_rate - self.config.slow_bullet_start_rate) * progress
            )

            # В критическом режиме увеличиваем частоту еще на 50%
            if effective_time > self.config.critical_time:
                current_rate *= 1.5

            return 1.0 / current_rate

        def update_attacks(self, current_time, critical_mode=False):
            """Обновляет все типы атак"""

            # 1. Обновляем пассивные медленные пули
            self.update_slow_bullets(current_time, critical_mode)

            # 2. Если нужно повторить атаку в критическом режиме
            if self.repeat_attack and current_time >= self.repeat_delay:
                self.execute_attack(self.last_attack_type)
                self.repeat_attack = False
                self.last_attack_time = current_time
                return

            # 3. Проверяем, можно ли запустить новую атаку
            attack_interval = self.get_current_attack_interval(current_time)

            if current_time - self.last_attack_time > attack_interval:
                attack_type = self.get_next_attack()
                self.execute_attack(attack_type)
                self.last_attack_type = attack_type
                self.last_attack_time = current_time

                # В критическом режиме планируем повтор атаки
                if critical_mode and random.random() < 0.7:
                    self.repeat_attack = True
                    self.repeat_delay = current_time + self.config.critical_attack_repeat_delay

        def update_slow_bullets(self, current_time, critical_mode=False):
            """Обновляет спавн медленных пуль"""
            # Учитываем начальную задержку
            if current_time < self.config.game_start_delay:
                return

            # Рассчитываем текущий интервал для медленных пуль
            slow_interval = self.get_current_slow_bullet_interval(current_time)

            # Проверяем, можно ли спавнить новую медленную пулю
            if current_time - self.last_slow_bullet_time > slow_interval:
                self.execute_slow_bullet()
                self.last_slow_bullet_time = current_time

        def execute_slow_bullet(self):
            """Создает медленную пулю через центр поля"""
            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            game_zone_x = sizes["padding"] + sizes["side_panel_width"]
            game_zone_y = sizes["top_panel_height"]
            game_zone_width = sizes["game_zone_width"]
            game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

            center_x = game_zone_x + game_zone_width // 2
            center_y = game_zone_y + game_zone_height // 2

            # Выбираем случайную сторону для спавна
            sides = ["left", "right", "top", "bottom"]
            start_side = random.choice(sides)

            # Определяем стартовую позицию за пределами поля
            if start_side == "left":
                start_x = game_zone_x - 100
                start_y = random.randint(game_zone_y - 50, game_zone_y + game_zone_height + 50)
                target_x = game_zone_x + game_zone_width + 100
                target_y = game_zone_y + game_zone_height - (start_y - game_zone_y)
            elif start_side == "right":
                start_x = game_zone_x + game_zone_width + 100
                start_y = random.randint(game_zone_y - 50, game_zone_y + game_zone_height + 50)
                target_x = game_zone_x - 100
                target_y = game_zone_y + game_zone_height - (start_y - game_zone_y)
            elif start_side == "top":
                start_x = random.randint(game_zone_x - 50, game_zone_x + game_zone_width + 50)
                start_y = game_zone_y - 100
                target_x = game_zone_x + game_zone_width - (start_x - game_zone_x)
                target_y = game_zone_y + game_zone_height + 100
            else:  # bottom
                start_x = random.randint(game_zone_x - 50, game_zone_x + game_zone_width + 50)
                start_y = game_zone_y + game_zone_height + 100
                target_x = game_zone_x + game_zone_width - (start_x - game_zone_x)
                target_y = game_zone_y - 100

            # Создаем медленную пулю
            slow_bullet = SlowBullet(
                self.config,
                start_x, start_y,
                target_x, target_y
            )

            self.game.bullets.append(slow_bullet)

        def execute_attack(self, attack_type):
            """Выполняет атаку определенного типа"""
            if attack_type == ATTACK_ARROWS_1:
                self.execute_arrows_1()
            elif attack_type == ATTACK_ARROWS_2:
                self.execute_arrows_2()
            elif attack_type == ATTACK_SPHERE_BURST:
                self.execute_sphere_burst()

        def execute_arrows_1(self):
            """Три параллельные стрелы - УМЕНЬШЕНО РАССТОЯНИЕ"""
            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            game_zone_x = sizes["padding"] + sizes["side_panel_width"]
            game_zone_y = sizes["top_panel_height"]
            game_zone_width = sizes["game_zone_width"]
            game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

            speed = self.config.arrow_speed * self.game.current_difficulty

            side = random.choice(["left", "right", "top", "bottom"])

            if side in ["left", "right"]:
                # Горизонтальные стрелы - БОЛЬШЕ ПУЛЬ БЛИЖЕ К ЦЕНТРУ
                start_y = random.randint(game_zone_y + 100, game_zone_y + game_zone_height - 100)
                step = int(game_zone_height * self.config.arrows_spacing)  # УМЕНЬШЕННОЕ РАССТОЯНИЕ

                for i in range(3):
                    y = start_y + (i - 1) * step

                    if side == "left":
                        arrow = ArrowBullet(
                            self.config,
                            game_zone_x - 50, y,
                            0, speed,
                            self.config.arrow_length,
                            self.config.arrow_width
                        )
                    else:
                        arrow = ArrowBullet(
                            self.config,
                            game_zone_x + game_zone_width + 50, y,
                            math.pi, speed,
                            self.config.arrow_length,
                            self.config.arrow_width
                        )
                    self.game.bullets.append(arrow)
            else:
                # Вертикальные стрелы - БОЛЬШЕ ПУЛЬ БЛИЖЕ К ЦЕНТРУ
                start_x = random.randint(game_zone_x + 100, game_zone_x + game_zone_width - 100)
                step = int(game_zone_width * self.config.arrows_spacing)  # УМЕНЬШЕННОЕ РАССТОЯНИЕ

                for i in range(3):
                    x = start_x + (i - 1) * step

                    if side == "top":
                        arrow = ArrowBullet(
                            self.config,
                            x, game_zone_y - 50,
                            math.pi/2, speed,
                            self.config.arrow_length,
                            self.config.arrow_width
                        )
                    else:
                        arrow = ArrowBullet(
                            self.config,
                            x, game_zone_y + game_zone_height + 50,
                            -math.pi/2, speed,
                            self.config.arrow_length,
                            self.config.arrow_width
                        )
                    self.game.bullets.append(arrow)

        def execute_arrows_2(self):
            """Пять стрел по дуге - ИСПРАВЛЕНА ТРАЕКТОРИЯ"""
            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            game_zone_x = sizes["padding"] + sizes["side_panel_width"]
            game_zone_y = sizes["top_panel_height"]
            game_zone_width = sizes["game_zone_width"]
            game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

            speed = self.config.arrow_speed * self.game.current_difficulty * 0.8

            side = random.choice(["top", "bottom", "left", "right"])

            if side in ["top", "bottom"]:
                # Стрелы летят сверху/снизу - ГАРАНТИРУЕМ ПРОХОЖДЕНИЕ ЧЕРЕЗ ПОЛЕ
                start_x = game_zone_x + game_zone_width // 2

                # Уменьшаем разброс углов, чтобы все пули попадали на поле
                if side == "top":
                    base_angle = math.radians(-45)  # Начинаем с -45 градусов
                    angle_step = math.radians(22.5)  # Уменьшенный шаг

                    for i in range(5):
                        angle = base_angle + i * angle_step
                        arrow = ArrowBullet(
                            self.config,
                            start_x, game_zone_y - 50,
                            angle, speed,
                            self.config.arrow_length,
                            self.config.arrow_width
                        )
                        self.game.bullets.append(arrow)
                else:
                    base_angle = math.radians(135)  # Начинаем с 135 градусов
                    angle_step = math.radians(22.5)  # Уменьшенный шаг

                    for i in range(5):
                        angle = base_angle + i * angle_step
                        arrow = ArrowBullet(
                            self.config,
                            start_x, game_zone_y + game_zone_height + 50,
                            angle, speed,
                            self.config.arrow_length,
                            self.config.arrow_width
                        )
                        self.game.bullets.append(arrow)
            else:
                # Стрелы летят слева/справа - ГАРАНТИРУЕМ ПРОХОЖДЕНИЕ ЧЕРЕЗ ПОЛЕ
                start_y = game_zone_y + game_zone_height // 2

                if side == "left":
                    base_angle = math.radians(-45)  # Начинаем с -45 градусов
                    angle_step = math.radians(22.5)  # Уменьшенный шаг

                    for i in range(5):
                        angle = base_angle + i * angle_step
                        arrow = ArrowBullet(
                            self.config,
                            game_zone_x - 50, start_y,
                            angle, speed,
                            self.config.arrow_length,
                            self.config.arrow_width
                        )
                        self.game.bullets.append(arrow)
                else:
                    base_angle = math.radians(135)  # Начинаем с 135 градусов
                    angle_step = math.radians(22.5)  # Уменьшенный шаг

                    for i in range(5):
                        angle = base_angle + i * angle_step
                        arrow = ArrowBullet(
                            self.config,
                            game_zone_x + game_zone_width + 50, start_y,
                            angle, speed,
                            self.config.arrow_length,
                            self.config.arrow_width
                        )
                        self.game.bullets.append(arrow)

        def execute_sphere_burst(self):
            """Шар из случайной точки на нижней границе"""
            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            game_zone_x = sizes["padding"] + sizes["side_panel_width"]
            game_zone_y = sizes["top_panel_height"]
            game_zone_width = sizes["game_zone_width"]
            game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

            # Случайная точка на нижней границе
            start_x = random.randint(game_zone_x + 100, game_zone_x + game_zone_width - 100)
            start_y = game_zone_y + game_zone_height + 50

            # Основной шар
            sphere = SphereBullet(
                self.config,
                start_x, start_y,
                int(renpy.config.screen_height * self.config.sphere_radius_ratio),
                self.config.colors["sphere_main"],
                0, -self.config.sphere_speed * self.game.current_difficulty,
                is_main=True
            )

            self.game.bullets.append(sphere)

            # Запланировать взрыв
            renpy.invoke_in_thread(self.delayed_explosion, sphere)

        def delayed_explosion(self, sphere):
            """Отложенный взрыв шара"""
            import time
            time.sleep(self.config.sphere_explosion_delay)

            if sphere in self.game.bullets and sphere.alive:
                sphere.alive = False
                renpy.invoke_in_main_thread(self.create_mini_spheres, sphere.x, sphere.y)

        def create_mini_spheres(self, x, y):
            """Создает мини-шары при взрыве"""
            for i in range(5):
                angle = math.radians(i * 72)
                mini_sphere = SphereBullet(
                    self.config,
                    x, y,
                    int(renpy.config.screen_height * self.config.mini_sphere_ratio),
                    self.config.colors["bullet_fill"],
                    math.cos(angle) * self.config.mini_sphere_speed * self.game.current_difficulty,
                    math.sin(angle) * self.config.mini_sphere_speed * self.game.current_difficulty,
                    is_main=False
                )
                self.game.bullets.append(mini_sphere)