# game/bullet_hell/player.rpy
init python:
    import pygame as pg
    import math
    import random

    class BulletHellPlayer(renpy.Displayable):
        def __init__(self, config, *args, **kwargs):
            super(BulletHellPlayer, self).__init__(*args, **kwargs)

            self.config = config
            self.color = config.colors["player"]
            self.size = int(renpy.config.screen_height * config.player_size_ratio)
            self.displayable = Solid(self.color, xsize=self.size, ysize=self.size)

            # Основное движение
            self.speed_x = 0
            self.speed_y = 0
            self.max_speed_x = config.player_speed[0] * renpy.config.screen_width / 1280 * 0.5
            self.max_speed_y = config.player_speed[1] * renpy.config.screen_height / 720 * 0.5

            # Рывок
            self.dash_distance = self.size * config.dash_distance_multiplier
            self.dash_cooldown = config.dash_cooldown
            self.dash_duration = config.dash_duration
            self.is_dashing = False
            self.dash_start_time = 0
            self.dash_direction_x = 0
            self.dash_direction_y = 0
            self.dash_cooldown_timer = 0
            self.dash_ready = True
            self.dash_from_x = 0
            self.dash_from_y = 0
            self.last_move_x = 0
            self.last_move_y = 0

            # Инициализация позиции
            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            game_zone_x = sizes["padding"] + sizes["side_panel_width"]
            game_zone_y = sizes["top_panel_height"]
            game_zone_width = sizes["game_zone_width"]
            game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

            self.x = game_zone_x + game_zone_width // 2 - self.size // 2
            self.y = game_zone_y + game_zone_height // 2 - self.size // 2

            # Состояние игрока
            self.old_st = None
            self.alive = True
            self.displayable_render = None
            self.max_lives = config.player_max_lives
            self.lives = self.max_lives
            self.last_hit_time = -10
            self.invincible_time = config.player_invincible_time
            self.invincible_flash_phase = 0.0
            self.is_invincible = False
            self.just_took_hit = False
            self.last_lives = self.max_lives

            # Эффекты от помощника - ПРОСТАЯ РЕАЛИЗАЦИЯ
            self.shield_active = False
            self.shield_end_time = 0
            self.time_slow_active = False
            self.time_slow_end_time = 0
            self.time_slow_radius = self.size * config.time_slow_radius_multiplier
            self.heal_animation_time = 0
            self.lost_life_flash_time = 0

        @property
        def width(self):
            return self.size

        @property
        def height(self):
            return self.size

        def overlaps_with(self, other):
            dx = abs((self.x + self.size/2) - (other.x + other.size/2))
            dy = abs((self.y + self.size/2) - (other.y + other.size/2))
            return dx < (self.size + other.size)/2.5 and dy < (self.size + other.size)/2.5

        def move_player(self):
            current_time = renpy.get_game_runtime()

            # Обновляем откат рывка
            if not self.dash_ready:
                self.dash_cooldown_timer = current_time - self.dash_start_time
                if self.dash_cooldown_timer >= self.dash_cooldown:
                    self.dash_ready = True

            # Если активен рывок
            if self.is_dashing:
                dash_progress = (current_time - self.dash_start_time) / self.dash_duration
                if dash_progress >= 1.0:
                    self.is_dashing = False
                    self.speed_x = 0
                    self.speed_y = 0
                else:
                    self.speed_x = 0
                    self.speed_y = 0
                    return

            # Обычное управление
            keys = pygame.key.get_pressed()
            self.last_move_x = 0
            self.last_move_y = 0

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.speed_y = -self.max_speed_y
                self.last_move_y = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.speed_y = self.max_speed_y
                self.last_move_y = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.speed_x = -self.max_speed_x
                self.last_move_x = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.speed_x = self.max_speed_x
                self.last_move_x = 1

            # Сброс скорости при отсутствии ввода
            if not (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_s] or keys[pygame.K_DOWN]):
                self.speed_y = 0
            if not (keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                self.speed_x = 0

            # Активация рывка
            if (keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]) and self.dash_ready and not self.is_dashing:
                self.activate_dash()

        def activate_dash(self):
            if self.last_move_x == 0 and self.last_move_y == 0:
                self.dash_direction_x = 1
                self.dash_direction_y = 0
            else:
                length = math.sqrt(self.last_move_x**2 + self.last_move_y**2)
                self.dash_direction_x = self.last_move_x / length
                self.dash_direction_y = self.last_move_y / length

            self.dash_from_x = self.x
            self.dash_from_y = self.y

            self.is_dashing = True
            self.dash_ready = False
            self.dash_start_time = renpy.get_game_runtime()
            self.last_hit_time = self.dash_start_time  # Неуязвимость во время рывка

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)

            if self.old_st is None:
                self.old_st = st

            dtime = st - self.old_st
            self.old_st = st

            current_time = renpy.get_game_runtime()
            time_since_hit = current_time - self.last_hit_time

            # Обновляем эффекты
            if self.shield_active and current_time >= self.shield_end_time:
                self.shield_active = False

            if self.time_slow_active and current_time >= self.time_slow_end_time:
                self.time_slow_active = False

            if self.heal_animation_time > 0:
                self.heal_animation_time = max(0, self.heal_animation_time - dtime)

            if self.lost_life_flash_time > 0:
                self.lost_life_flash_time = max(0, self.lost_life_flash_time - dtime)

            # Проверяем состояние неуязвимости
            self.is_invincible = (time_since_hit < self.invincible_time or self.shield_active)

            if self.is_invincible:
                self.invincible_flash_phase = (math.sin(current_time * 15) + 1) / 2
            else:
                self.invincible_flash_phase = 1.0

            # Движение игрока
            if self.alive:
                self.move_player()

                if self.is_dashing:
                    dash_progress = (current_time - self.dash_start_time) / self.dash_duration
                    if dash_progress < 1.0:
                        progress = dash_progress
                        ease_progress = 1 - (1 - progress) ** 2
                        self.x = self.dash_from_x + self.dash_direction_x * self.dash_distance * ease_progress
                        self.y = self.dash_from_y + self.dash_direction_y * self.dash_distance * ease_progress
                else:
                    self.x += self.speed_x * dtime
                    self.y += self.speed_y * dtime

                # Ограничение в пределах игровой зоны
                global sizes
                game_zone_x = sizes["padding"] + sizes["side_panel_width"]
                game_zone_y = sizes["top_panel_height"]
                game_zone_width = sizes["game_zone_width"]
                game_zone_height = sizes["screen_height"] - sizes["top_panel_height"] - sizes["bottom_panel_height"]

                self.x = max(game_zone_x, min(self.x, game_zone_x + game_zone_width - self.size))
                self.y = max(game_zone_y, min(self.y, game_zone_y + game_zone_height - self.size))

            # Рисуем эффекты - ПРОСТАЯ ВЕРСИЯ БЕЗ CIRCLE
            if self.time_slow_active:
                # Просто рисуем полупрозрачный прямоугольник вместо круга
                slow_rect = Solid(self.config.colors["time_slow"] + "40",
                                xsize=int(self.time_slow_radius * 2),
                                ysize=int(self.time_slow_radius * 2))
                slow_render = renpy.render(slow_rect,
                                          self.time_slow_radius * 2,
                                          self.time_slow_radius * 2, st, at)
                render.blit(slow_render, (self.x + self.size/2 - self.time_slow_radius,
                                         self.y + self.size/2 - self.time_slow_radius))

            if self.shield_active:
                # Просто рисуем полупрозрачный прямоугольник вместо круга
                shield_size = self.size * self.config.shield_size_multiplier
                shield_rect = Solid(self.config.colors["shield"] + "80",
                                  xsize=int(shield_size * 2),
                                  ysize=int(shield_size * 2))
                shield_render = renpy.render(shield_rect,
                                            shield_size * 2,
                                            shield_size * 2, st, at)
                render.blit(shield_render, (self.x + self.size/2 - shield_size,
                                           self.y + self.size/2 - shield_size))

            # Рисуем игрока с миганием при неуязвимости
            if self.is_invincible:
                if int(current_time * 8) % 2 == 0:
                    self.displayable_render = renpy.render(self.displayable, width, height, st, at)
                    if self.alive:
                        render.blit(self.displayable_render, (self.x, self.y))
            else:
                self.displayable_render = renpy.render(self.displayable, width, height, st, at)
                if self.alive:
                    render.blit(self.displayable_render, (self.x, self.y))

            renpy.redraw(self, 0.01)
            return render

        def take_hit(self, current_time):
            if not self.is_dashing and not self.is_invincible:
                self.lives -= 1
                self.last_hit_time = current_time
                self.just_took_hit = True
                self.lost_life_flash_time = 1.0
                return True
            return False

        def heal(self, amount=1):
            if self.lives < self.max_lives:
                self.lives = min(self.max_lives, self.lives + amount)
                self.heal_animation_time = 1.0
                return True
            return False

        def activate_shield(self, duration=3.0):
            current_time = renpy.get_game_runtime()
            self.shield_active = True
            self.shield_end_time = current_time + duration
            self.last_hit_time = current_time

        def activate_time_slow(self, duration=3.0):
            current_time = renpy.get_game_runtime()
            self.time_slow_active = True
            self.time_slow_end_time = current_time + duration

        def reset_hit_flag(self):
            self.just_took_hit = False

        def event(self, ev, x, y, st):
            if not self.alive:
                return True
            raise renpy.IgnoreEvent()