# game/bullet_hell/game.rpy
init python:
    import pygame
    import math

    class BulletHellGame(renpy.Displayable):
        def __init__(self, *args, **kwargs):
            super(BulletHellGame, self).__init__(*args, **kwargs)

            global sizes
            sizes = calculate_sizes()

            # Конфигурация
            self.config = BulletHellConfig()

            # Игровые объекты
            self.player = BulletHellPlayer(self.config)
            self.assistant = Assistant(self.config)
            self.attack_manager = AttackManager(self.config, self)

            # Состояние игры
            self.bullets = []
            self.game_over = False
            self.game_over_time = None
            self.time_elapsed = 0.0
            self.victory = False
            self.game_start_time = renpy.get_game_runtime()
            self.critical_time_reached = False
            self.current_difficulty = 1.0
            self.music_started = False
            self.game_start_delay = self.config.game_start_delay  # 3 секунды задержки перед началом атак

            # Интерфейс
            self.assistant_message = ""
            self.message_end_time = 0

        def check_collisions(self):
            """Упрощенная проверка столкновений"""
            current_time = renpy.get_game_runtime()

            if not self.player.alive or self.player.is_invincible:
                return False

            player_x = self.player.x + self.player.size/2
            player_y = self.player.y + self.player.size/2
            player_radius = self.player.size/2

            for bullet in self.bullets:
                if not bullet.alive or bullet.hit_registered:
                    continue

                # Простая проверка расстояния между центрами
                dx = player_x - bullet.x
                dy = player_y - bullet.y
                distance_squared = dx*dx + dy*dy

                # Определяем радиус пули
                if hasattr(bullet, 'radius'):
                    bullet_radius = bullet.radius
                elif hasattr(bullet, 'width'):
                    bullet_radius = bullet.width * 0.8
                else:
                    bullet_radius = 10  # Значение по умолчанию

                # Проверяем столкновение
                if distance_squared < (player_radius + bullet_radius) ** 2:
                    if self.player.take_hit(current_time):
                        bullet.hit_registered = True
                        bullet.alive = False

                        if self.player.lives <= 0:
                            self.player.alive = False
                            self.game_over = True
                            self.game_over_time = current_time
                            self.victory = False

                        return True

            return False

        def update_difficulty(self):
            current_time = renpy.get_game_runtime()
            self.time_elapsed = current_time - self.game_start_time

            # Запуск музыки
            if not self.music_started and self.time_elapsed > 0.1:
                renpy.music.play("audio/heaven.mp3", channel="music", loop=True, fadein=1.0)
                self.music_started = True

            # Учитываем начальную задержку
            effective_time = max(0, self.time_elapsed - self.game_start_delay)

            if effective_time == 0:
                self.current_difficulty = 1.0
                return

            time_factor = min(1.8, 1.0 + effective_time / 80.0)

            if effective_time > self.config.critical_time and not self.critical_time_reached:
                self.critical_time_reached = True
                self.current_difficulty = 1.8
            elif effective_time > self.config.critical_time:
                critical_factor = 1.0 + (effective_time - self.config.critical_time) / 40.0
                self.current_difficulty = 1.8 * min(1.5, critical_factor)
            else:
                self.current_difficulty = time_factor

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)

            current_time = renpy.get_game_runtime()
            self.time_elapsed = current_time - self.game_start_time

            # Проверка окончания игры по времени (учитываем задержку)
            if not self.game_over and (self.time_elapsed - self.game_start_delay) >= self.config.game_duration:
                self.game_over = True
                self.game_over_time = current_time
                self.victory = True

            self.update_difficulty()

            # Обновляем помощника (только если игра не окончена)
            if not self.game_over:
                ability_used = self.assistant.update(
                    st - (self.assistant.old_st or 0),
                    current_time,
                    self.player.lives,
                    self.player.max_lives,
                    self.player.just_took_hit
                )

                if ability_used == 1:
                    if self.player.heal(1):
                        self.assistant_message = "Ты справишься!"
                        self.message_end_time = current_time + 2.0
                elif ability_used == 2:
                    self.player.activate_shield(3.0)
                    self.assistant_message = "Ты выдержишь!"
                    self.message_end_time = current_time + 2.0
                elif ability_used == 3:
                    self.player.activate_time_slow(3.0)
                    self.assistant_message = "Ты не проиграешь!"
                    self.message_end_time = current_time + 2.0

                self.player.reset_hit_flag()

            # Обновляем сообщение помощника
            if current_time >= self.message_end_time:
                self.assistant_message = ""

            # Добавляем атаки только после начальной задержки и если игра не окончена
            if not self.game_over and self.time_elapsed > self.game_start_delay:
                self.attack_manager.update_attacks(current_time, self.critical_time_reached)

            # Проверяем столкновения только если игра не окончена
            if not self.game_over:
                self.check_collisions()

            # Применяем замедление времени
            if not self.game_over and self.player.time_slow_active:
                for bullet in self.bullets:
                    if bullet.alive:
                        bullet.apply_time_slow(
                            self.player.x + self.player.size/2,
                            self.player.y + self.player.size/2,
                            self.player.time_slow_radius
                        )

            # Рендерим помощника
            try:
                assistant_render = self.assistant.render(width, height, st, at)
                render.blit(assistant_render, (0, 0))
            except:
                pass

            # Рендерим игрока
            try:
                player_render = self.player.render(width, height, st, at)
                render.blit(player_render, (0, 0))
            except:
                pass

            # Рендерим пули
            bullets_to_remove = []
            for i, bullet in enumerate(self.bullets):
                if bullet.alive:
                    try:
                        bullet_render = bullet.render(width, height, st, at)
                        render.blit(bullet_render, (0, 0))
                    except Exception as e:
                        bullets_to_remove.append(i)
                else:
                    bullets_to_remove.append(i)

            for i in sorted(bullets_to_remove, reverse=True):
                if i < len(self.bullets):
                    self.bullets.pop(i)

            if self.game_over and self.game_over_time:
                if current_time - self.game_over_time > 1.0:
                    renpy.timeout(0)

            renpy.redraw(self, 0.01)
            return render

        def event(self, ev, x, y, st):
            if not self.game_over:
                result = self.player.event(ev, x, y, st)
                if result:
                    return result

            raise renpy.IgnoreEvent()