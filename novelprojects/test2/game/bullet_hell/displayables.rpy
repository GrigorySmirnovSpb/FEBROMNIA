# game/bullet_hell/displayables.rpy
init python:
    import pygame
    import math

    class Circle(renpy.Displayable):
        """Круглый эффект для щита и замедления времени"""
        def __init__(self, radius, color, *args, **kwargs):
            super(Circle, self).__init__(*args, **kwargs)
            self.radius = radius
            self.color = color

        def render(self, width, height, st, at):
            render = renpy.Render(self.radius * 2, self.radius * 2)

            # Создаем поверхность
            circle_surface = renpy.display.pgrender.surface((self.radius * 2, self.radius * 2), True)

            # Рисуем круг
            pygame.draw.circle(circle_surface, renpy.easy.color(self.color),
                             (self.radius, self.radius), self.radius)

            render.blit(circle_surface, (0, 0))
            return render

    class ArrowBullet(renpy.Displayable):
        """Прямоугольная стрела (узкой стороной вперед)"""
        def __init__(self, config, start_x, start_y, angle, speed, length, width, *args, **kwargs):
            super(ArrowBullet, self).__init__(*args, **kwargs)

            self.config = config
            self.length = int(renpy.config.screen_height * length)  # Длинная сторона
            self.width = int(renpy.config.screen_height * width)    # Короткая сторона
            self.x = start_x
            self.y = start_y
            self.angle = angle
            self.speed = speed
            self.speed_x = math.cos(angle) * speed
            self.speed_y = math.sin(angle) * speed

            self.old_st = None
            self.alive = True
            self.hit_registered = False
            self.start_time = renpy.get_game_runtime()
            self.max_lifetime = config.bullet_max_lifetime
            self.slow_factor = 1.0
            self.original_speed = speed

        def apply_time_slow(self, player_x, player_y, player_slow_radius):
            dx = self.x - player_x
            dy = self.y - player_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < player_slow_radius:
                self.slow_factor = self.config.time_slow_factor
            else:
                self.slow_factor = 1.0

            self.speed = self.original_speed * self.slow_factor
            self.speed_x = math.cos(self.angle) * self.speed
            self.speed_y = math.sin(self.angle) * self.speed

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)

            if self.old_st is None:
                self.old_st = st

            dtime = st - self.old_st
            self.old_st = st

            # Обновляем позицию
            self.x += self.speed_x * dtime
            self.y += self.speed_y * dtime

            # Создаем прямоугольник стрелы
            arrow_surface = renpy.display.pgrender.surface((self.length, self.width), True)

            # Рисуем обводку
            pygame.draw.rect(arrow_surface, renpy.easy.color(self.config.colors["bullet_outline"]),
                           (0, 0, self.length, self.width))

            # Рисуем заливку
            pygame.draw.rect(arrow_surface, renpy.easy.color(self.config.colors["bullet_fill"]),
                           (2, 2, self.length-4, self.width-4))

            # Поворачиваем поверхность в направлении движения
            try:
                rotated_surface = pygame.transform.rotate(arrow_surface, -math.degrees(self.angle))
                rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))

                render.blit(rotated_surface, (rotated_rect.x, rotated_rect.y))
            except:
                # Если ошибка при повороте, рисуем без поворота
                render.blit(arrow_surface, (self.x - self.length//2, self.y - self.width//2))

            # Проверяем выход за границы
            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            game_zone_x = sizes["padding"] + sizes["side_panel_width"]
            game_zone_y = sizes["top_panel_height"]
            game_zone_width = sizes["game_zone_width"]
            game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

            margin = max(game_zone_width, game_zone_height) * 0.5

            if (self.y > game_zone_y + game_zone_height + margin or
                self.y < game_zone_y - margin or
                self.x > game_zone_x + game_zone_width + margin or
                self.x < game_zone_x - margin):
                self.alive = False

            if renpy.get_game_runtime() - self.start_time > self.max_lifetime:
                self.alive = False

            renpy.redraw(self, 0.01)
            return render

    class SphereBullet(renpy.Displayable):
        """Сферическая пуля"""
        def __init__(self, config, start_x, start_y, radius, color, speed_x, speed_y, is_main=False, *args, **kwargs):
            super(SphereBullet, self).__init__(*args, **kwargs)

            self.config = config
            self.radius = radius
            self.x = start_x
            self.y = start_y
            self.speed_x = speed_x
            self.speed_y = speed_y
            self.color = color
            self.is_main = is_main

            self.old_st = None
            self.alive = True
            self.hit_registered = False
            self.start_time = renpy.get_game_runtime()
            self.max_lifetime = config.bullet_max_lifetime
            self.slow_factor = 1.0
            self.original_speed_x = speed_x
            self.original_speed_y = speed_y

        def apply_time_slow(self, player_x, player_y, player_slow_radius):
            dx = self.x - player_x
            dy = self.y - player_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < player_slow_radius:
                self.slow_factor = self.config.time_slow_factor
            else:
                self.slow_factor = 1.0

            self.speed_x = self.original_speed_x * self.slow_factor
            self.speed_y = self.original_speed_y * self.slow_factor

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)

            if self.old_st is None:
                self.old_st = st

            dtime = st - self.old_st
            self.old_st = st

            # Обновляем позицию
            self.x += self.speed_x * dtime
            self.y += self.speed_y * dtime

            # Рисуем шар
            circle_surface = renpy.display.pgrender.surface((self.radius * 2, self.radius * 2), True)

            # Для основного шара - немного больше обводка
            outline_width = 3 if self.is_main else 2

            # Обводка
            pygame.draw.circle(circle_surface, renpy.easy.color(self.config.colors["bullet_outline"]),
                             (self.radius, self.radius), self.radius)

            # Заливка
            pygame.draw.circle(circle_surface, renpy.easy.color(self.color),
                             (self.radius, self.radius), self.radius - outline_width)

            render.blit(circle_surface, (self.x - self.radius, self.y - self.radius))

            # Проверяем выход за границы
            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            game_zone_x = sizes["padding"] + sizes["side_panel_width"]
            game_zone_y = sizes["top_panel_height"]
            game_zone_width = sizes["game_zone_width"]
            game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

            margin = max(game_zone_width, game_zone_height) * 0.5

            if (self.y > game_zone_y + game_zone_height + margin or
                self.y < game_zone_y - margin or
                self.x > game_zone_x + game_zone_width + margin or
                self.x < game_zone_x - margin):
                self.alive = False

            if renpy.get_game_runtime() - self.start_time > self.max_lifetime:
                self.alive = False

            renpy.redraw(self, 0.01)
            return render

    class SlowBullet(renpy.Displayable):
        """Медленная круглая пуля размером с игрока"""
        def __init__(self, config, start_x, start_y, target_x, target_y, *args, **kwargs):
            super(SlowBullet, self).__init__(*args, **kwargs)

            self.config = config
            self.radius = int(renpy.config.screen_height * config.slow_bullet_size_ratio)
            self.x = start_x
            self.y = start_y

            # Рассчитываем скорость к цели
            dx = target_x - start_x
            dy = target_y - start_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                speed = config.slow_bullet_speed
                self.speed_x = (dx / distance) * speed
                self.speed_y = (dy / distance) * speed
            else:
                self.speed_x = 0
                self.speed_y = 0

            self.angle = math.atan2(dy, dx) if distance > 0 else 0

            self.old_st = None
            self.alive = True
            self.hit_registered = False
            self.start_time = renpy.get_game_runtime()
            self.max_lifetime = config.bullet_max_lifetime
            self.slow_factor = 1.0
            self.original_speed_x = self.speed_x
            self.original_speed_y = self.speed_y

        def apply_time_slow(self, player_x, player_y, player_slow_radius):
            dx = self.x - player_x
            dy = self.y - player_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < player_slow_radius:
                self.slow_factor = self.config.time_slow_factor
            else:
                self.slow_factor = 1.0

            self.speed_x = self.original_speed_x * self.slow_factor
            self.speed_y = self.original_speed_y * self.slow_factor

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)

            if self.old_st is None:
                self.old_st = st

            dtime = st - self.old_st
            self.old_st = st

            # Обновляем позицию
            self.x += self.speed_x * dtime
            self.y += self.speed_y * dtime

            # Рисуем круглую пулю
            circle_surface = renpy.display.pgrender.surface((self.radius * 2, self.radius * 2), True)

            # Обводка
            pygame.draw.circle(circle_surface, renpy.easy.color(self.config.colors["bullet_outline"]),
                             (self.radius, self.radius), self.radius)

            # Заливка
            pygame.draw.circle(circle_surface, renpy.easy.color(self.config.colors["bullet_fill"]),
                             (self.radius, self.radius), self.radius - 2)

            render.blit(circle_surface, (self.x - self.radius, self.y - self.radius))

            # Проверяем выход за границы
            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            game_zone_x = sizes["padding"] + sizes["side_panel_width"]
            game_zone_y = sizes["top_panel_height"]
            game_zone_width = sizes["game_zone_width"]
            game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

            margin = max(game_zone_width, game_zone_height) * 0.5

            if (self.y > game_zone_y + game_zone_height + margin or
                self.y < game_zone_y - margin or
                self.x > game_zone_x + game_zone_width + margin or
                self.x < game_zone_x - margin):
                self.alive = False

            if renpy.get_game_runtime() - self.start_time > self.max_lifetime:
                self.alive = False

            renpy.redraw(self, 0.01)
            return render