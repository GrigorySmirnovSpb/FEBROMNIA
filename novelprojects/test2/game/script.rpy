# script.rpy - Объединенный сценарий

init python:
    # Функция звука печатания текста (из новеллы)
    def type_sound(event, interact=True, **kwargs):
        if not interact:
            return
        if event == "begin":
            for i in range(50):
                renpy.sound.queue("audio/sound.mp3")
        elif event == "slow_done":
            renpy.sound.stop()

# Определяем персонажей (из новеллы) - ВАЖНО: это ДО label start!
define selen = Character('Селена', color="#00FFFF", what_slow_cps=20, callback=type_sound)
define you = Character('', color="#4169e1", what_slow_cps=20, callback=type_sound)
define narrator = Character(None, kind=nvl)

# Определяем изображения (из новеллы)
image bg moon = Movie(
        play="video/moon.webm",
        pos=(0.5, 0.5),
        anchor=(0.5, 0.5),
        loop=True,
        channel="movie_atrop"
    )

image bg end = "images/end.jpg"

# Начало игры
label start:
    scene bg moon at Transform(zoom=2.5) with dissolve
    play music "audio/night.mp3" loop volume 0.5

    show selen at Transform(pos=(0.27, 0.08)) with dissolve:
        zoom 1.4

    # СУПЕР КОРОТКИЙ ДИАЛОГ
    selen "Приготовься к битве."

    you "Что?"

    selen "Твои страхи становятся реальностью."
    selen "Выдержишь испытание - найдешь свободу."
    selen "Проиграешь - останешься здесь навсегда."

    # Убираем меню выбора и сразу запускаем мини-игру
    you "Ладно... Я готов."

    # Останавливаем текущую музыку
    stop music fadeout 1.0

    # Переход к мини-игре
    selen "Начинаем."

    # Эффект дрожания экрана
    show selen:
        linear 0.1 xoffset 5
        linear 0.1 xoffset -5
        linear 0.1 xoffset 3
        linear 0.1 xoffset -3
        linear 0.1 xoffset 0

    # Текст перед битвой
    scene black
    show expression Text("НАЧАЛО БИТВЫ", size=72, color="#FF0000", bold=True) as text1:
        alpha 0.0
        xalign 0.5 yalign 0.5
        linear 0.5 alpha 1.0
        pause 0.5
        linear 0.5 alpha 0.0

    pause 1.0

    # Запуск мини-игры
    $ bullet_hell_game = BulletHellGame()
    call screen bullet_hell_game_screen(bullet_hell_game)

    # Останавливаем музыку из мини-игры
    stop music fadeout 2.0

    # Переход к соответствующей концовке
    if bullet_hell_game.victory:
        jump happy_ending
    else:
        jump bad_ending

    return

label happy_ending:
    scene black with dissolve

    # Эффект победы
    show expression Text("ПОБЕДА", size=72, color="#00FF00", bold=True) as victory_text:
        alpha 0.0
        xalign 0.5 yalign 0.3
        linear 0.5 alpha 1.0
        pause 1.0
        linear 0.5 alpha 0.0

    pause 1.5

    # Возвращаем Селену для финального диалога
    scene black with dissolve
    you "Я выдержал испытание!"

    # Показываем Селену снова
    scene bg moon at Transform(zoom=2.5) with dissolve
    show selen at Transform(pos=(0.27, 0.08)):
        zoom 1.4

    selen "Ты доказал свою силу. Ты готов встретиться с реальностью."
    selen "Прощай..."

    hide selen with dissolve

    # Финальная сцена
    scene bg end:
        fit "cover"
    with dissolve

    play music "audio/night.mp3" fadein 2.0 volume 0.3

    you "Ты просыпаешься. Комната озаряет солнечный свет. За окном поют весенние птицы."
    you "Мир и не так плох."
    you "Катарсис."
    you "Настоящая свобода начинается сейчас..."

    return

label bad_ending:
    scene black with dissolve

    # Эффект поражения
    show expression Text("ПОРАЖЕНИЕ", size=72, color="#FF0000", bold=True) as defeat_text:
        alpha 0.0
        xalign 0.5 yalign 0.3
        linear 0.5 alpha 1.0
        pause 1.0
        linear 0.5 alpha 0.0

    pause 1.5

    # Возвращаем Селену для финального диалога
    scene black with dissolve
    you "Я не смог... Я не выдержал..."

    # Показываем Селену снова
    scene bg moon at Transform(zoom=2.5) with dissolve
    show selen at Transform(pos=(0.27, 0.08)):
        zoom 1.4

    selen "Ты пал. Твои страхи оказались сильнее."
    selen "Теперь ты останешься здесь. Навсегда."

    hide selen with dissolve

    # Финальная сцена
    scene bg end:
        fit "cover"
    with dissolve

    play music "audio/night.mp3" fadein 2.0 volume 0.3

    you "Ты остаешься с ней. Обнимаешь ее. Вы плачете."
    you "Вы медленно каменеете, становитесь статуями."
    you "Ты решил навсегда остаться в этом мире."
    you "Вечность безвременья..."

    return