# game/bullet_hell/assistant.rpy
init python:
    import pygame
    import math
    import pygame as pg

    class Assistant(renpy.Displayable):
        def __init__(self, config, *args, **kwargs):
            super(Assistant, self).__init__(*args, **kwargs)

            self.config = config

            global sizes
            if sizes is None:
                sizes = calculate_sizes()

            # Размеры помощника
            self.radius = int(renpy.config.screen_height * config.assistant_size_ratio)
            self.base_color = config.colors["assistant_base"]
            self.active_color = config.colors["assistant_active"]
            self.current_color = self.base_color

            # Позиция в правом нижнем углу
            self.x = sizes["screen_width"] - sizes["padding"] - self.radius * 2
            self.y = sizes["screen_height"] - sizes["bottom_panel_height"] - self.radius * 2

            # Способности
            self.ability_cooldowns = [0, 0, 0]
            self.ability_durations = [0, 0, 0]
            self.ability_messages = ["", "", ""]
            self.last_ability_time = 0
            self.min_time_between_abilities = config.min_time_between_abilities

            # Анимации
            self.pulse_phase = 0
            self.pulse_speed = 2.0
            self.is_active = False
            self.active_end_time = 0
            self.old_st = None

        def update(self, dtime, current_time, player_lives, max_lives, player_took_hit):
            # Обновляем откаты способностей
            for i in range(3):
                if self.ability_cooldowns[i] > 0:
                    self.ability_cooldowns[i] = max(0, self.ability_cooldowns[i] - dtime)

            # Обновляем длительности активных способностей
            for i in range(3):
                if self.ability_durations[i] > 0:
                    self.ability_durations[i] = max(0, self.ability_durations[i] - dtime)
                    if self.ability_durations[i] <= 0:
                        self.ability_messages[i] = ""

            # Проверяем, можно ли использовать способности
            can_use_ability = (current_time - self.last_ability_time >= self.min_time_between_abilities)
            ability_used = False

            # Способность 1: Восстановление здоровья
            if (not ability_used and can_use_ability and
                player_lives < 3 and self.ability_cooldowns[0] <= 0):
                self.activate_ability(0, current_time, "Ты справишься!")
                ability_used = True
                return 1

            # Способность 2: Щит неуязвимости
            elif (not ability_used and can_use_ability and
                  player_took_hit and self.ability_cooldowns[1] <= 0):
                self.activate_ability(1, current_time, "Ты выдержишь!")
                ability_used = True
                return 2

            # Способность 3: Замедление времени
            elif (not ability_used and can_use_ability and
                  player_lives == 1 and self.ability_cooldowns[2] <= 0):
                self.activate_ability(2, current_time, "Ты не проиграешь!")
                ability_used = True
                return 3

            return 0

        def activate_ability(self, ability_index, current_time, message):
            self.ability_cooldowns[ability_index] = self.config.ability_cooldowns[ability_index]
            self.ability_durations[ability_index] = self.config.ability_durations[ability_index]
            self.ability_messages[ability_index] = message
            self.last_ability_time = current_time
            self.is_active = True
            self.active_end_time = current_time + 1.0

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)

            if self.old_st is None:
                self.old_st = st

            dtime = st - self.old_st
            self.old_st = st

            current_time = renpy.get_game_runtime()

            # Обновляем пульсацию
            self.pulse_phase += self.pulse_speed * dtime

            # Проверяем активное свечение
            if self.is_active and current_time >= self.active_end_time:
                self.is_active = False

            # Выбираем цвет
            if self.is_active:
                pulse_factor = (math.sin(self.pulse_phase) + 1) / 2
                r1, g1, b1 = int(self.base_color[1:3], 16), int(self.base_color[3:5], 16), int(self.base_color[5:7], 16)
                r2, g2, b2 = int(self.active_color[1:3], 16), int(self.active_color[3:5], 16), int(self.active_color[5:7], 16)

                r = int(r1 + (r2 - r1) * pulse_factor)
                g = int(g1 + (g2 - g1) * pulse_factor)
                b = int(b1 + (b2 - b1) * pulse_factor)

                self.current_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
            else:
                self.current_color = self.base_color

            # Рисуем помощника
            circle_surface = renpy.display.pgrender.surface((self.radius * 2, self.radius * 2), True)

            # ИСПРАВЛЕНИЕ: используем pygame напрямую
            pygame.draw.circle(circle_surface, renpy.easy.color(self.current_color),
                             (self.radius, self.radius), self.radius)

            # Обводка
            pygame.draw.circle(circle_surface, renpy.easy.color("#000000"),
                             (self.radius, self.radius), self.radius, 2)

            render.blit(circle_surface, (self.x, self.y))

            renpy.redraw(self, 0.01)
            return render

        def event(self, ev, x, y, st):
            raise renpy.IgnoreEvent()