# game/bullet_hell/screen.rpy
init python:
    pass

screen bullet_hell_game_screen(game):
    modal True

    python:
        if sizes is None:
            sizes = calculate_sizes()

        screen_width = sizes["screen_width"]
        screen_height = sizes["screen_height"]
        padding = sizes["padding"]
        side_panel_width = sizes["side_panel_width"]
        top_panel_height = sizes["top_panel_height"]
        bottom_panel_height = sizes["bottom_panel_height"]
        game_zone_width = sizes["game_zone_width"]

        game_zone_x = padding + side_panel_width
        game_zone_y = top_panel_height
        game_zone_height = screen_height - top_panel_height - bottom_panel_height

    # 1. Фон
    if game.config.background_image:
        add game.config.background_image:
            xsize screen_width
            ysize screen_height
            fit "fill"

    # 2. Игровая зона
    add Solid(game.config.game_zone_color):
        xpos game_zone_x
        ypos game_zone_y
        xsize game_zone_width
        ysize game_zone_height

    # 3. Рамка вокруг игровой зоны
    frame:
        pos (game_zone_x, game_zone_y)
        xsize game_zone_width
        ysize game_zone_height
        background Frame(Solid("#FFFFFF"), 2, 2, 2, 2)

    # 4. Сама игра
    add game

    # 5. Панель жизней
    frame:
        pos (padding, padding // 2)
        background Solid(game.config.colors["ui_background"])
        padding (10, 10)
        xsize side_panel_width - 20
        ysize int(top_panel_height * 0.6)

        vbox:
            spacing 5
            text "ЖИЗНИ" size min(14, int(screen_height * 0.02)) color game.config.colors["ui_text"] bold True xalign 0.5

            hbox:
                xalign 0.5
                spacing 10
                for i in range(3):
                    if i < game.player.lives:
                        add Solid(game.config.colors["life_full"],
                                 xsize=int(screen_height * 0.02),
                                 ysize=int(screen_height * 0.02)):
                            xalign 0.5
                    else:
                        $ current_time = renpy.get_game_runtime()
                        if i == game.player.lives and game.player.lost_life_flash_time > 0:
                            $ flash_phase = int(current_time * 10) % 2
                            if flash_phase == 0:
                                add Solid("#0000FF",
                                         xsize=int(screen_height * 0.02),
                                         ysize=int(screen_height * 0.02)):
                                    xalign 0.5
                            else:
                                add Solid(game.config.colors["life_full"],
                                         xsize=int(screen_height * 0.02),
                                         ysize=int(screen_height * 0.02)):
                                    xalign 0.5
                        elif i == game.player.lives and game.player.heal_animation_time > 0:
                            $ heal_phase = int(current_time * 8) % 2
                            if heal_phase == 0:
                                add Solid("#00FF00",
                                         xsize=int(screen_height * 0.02),
                                         ysize=int(screen_height * 0.02)):
                                    xalign 0.5
                            else:
                                add Solid(game.config.colors["life_full"],
                                         xsize=int(screen_height * 0.02),
                                         ysize=int(screen_height * 0.02)):
                                    xalign 0.5
                        else:
                            add Solid(game.config.colors["life_empty"],
                                     xsize=int(screen_height * 0.02),
                                     ysize=int(screen_height * 0.02)):
                                xalign 0.5

    # 6. Прогресс-бар времени (упрощенный)
    frame:
        pos (padding + side_panel_width, screen_height - bottom_panel_height)
        background Solid("#111111DD")
        padding (5, 5)
        xsize game_zone_width
        ysize bottom_panel_height - 10

        add Solid(game.config.colors["progress_background"],
                 xsize=game_zone_width - 10,
                 ysize=bottom_panel_height - 20):
            pos (5, 5)

        # Учитываем начальную задержку 3 секунды
        $ effective_time = max(0, game.time_elapsed - game.game_start_delay)
        $ total_duration = game.config.game_duration
        $ progress = min(1.0, effective_time / total_duration if total_duration > 0 else 0)
        $ dot_position = int((game_zone_width - 30) * progress)

        add Solid(game.config.colors["progress_marker"],
                 xsize=int(screen_height * 0.02),
                 ysize=int(screen_height * 0.02)):
            pos (10 + dot_position, (bottom_panel_height - 20 - int(screen_height * 0.02)) // 2)

        # Отметка критического времени
        $ critical_progress = min(1.0, (game.config.critical_time + 3.0) / (total_duration + 3.0))
        $ critical_pos = int((game_zone_width - 30) * critical_progress)
        add Solid(game.config.colors["progress_critical"], xsize=3, ysize=int(bottom_panel_height * 0.7)):
            pos (10 + critical_pos, (bottom_panel_height - 20) // 4)

    # 7. Сообщение помощника
    if game.assistant_message:
        frame:
            xalign 0.5
            yalign 0.2
            background Solid("#87CEEBAA")
            padding (15, 10)

            text "[game.assistant_message]" size min(18, int(screen_height * 0.025)) color "#FFFFFF" bold True

    # 8. Таймеры обновления
    timer 0.01 repeat True action renpy.restart_interaction
    timer 0.01 action If(game.game_over, Return()) repeat True