init python:
    def type_sound(event, interact=True, **kwargs):
        if not interact:
            return

        if event == "begin":
            for i in range(50):
                renpy.sound.queue("audio/sound.mp3")
        elif event == "slow_done":
            renpy.sound.stop()

define atropos = Character('Атропос', color="#9370db", what_slow_cps=20, callback=type_sound)
define noname = Character('Потерянный', color="#4169e1", what_slow_cps=20, callback=type_sound)

image bg uni = "images/uni.png"
image atropvid = Movie(
        play="atrop/atropvid.webm",
        pos=(0.5, 0.5),
        anchor=(0.5, 0.5),
        loop=True,
        channel="movie_atrop"
    )

label start:

    show expression Transform(Movie(play="stars.webm"), size=(1920, 1080)) as movie
    $ renpy.pause(4)
    hide movie

    scene bg uni:
       fit "cover"
    with dissolve

    play music "audio/ambient.mp3" loop volume 0.3

    "Мир"

    show atrop at center with dissolve:
        zoom 2

    atropos "Приветствую тебя"

    noname "Кто ты?"

    menu:
        "Бог":
            atropos "Сущность сущестсвующая вне мира"

        "Не твое дело":
            atropos "Моя природа не должна тебя волновать"

    noname "Понятно"

    return
