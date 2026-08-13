extends CharacterBody2D

const SPEED = 3500
@onready var anim = $AnimSelene
@onready var player = $"../Player"

var direction: Vector2 = Vector2(0, 0)
var f_in_selene_area = false
var next_position = Vector2.ZERO
var ind_move: int = 0

func _ready() -> void:
	next_position = player.global_position

func _physics_process(delta: float) -> void:
	if f_in_selene_area == true && Input.is_action_pressed("action"):
		Dialogic.start("res://dialogues/test1.dtl")
	if not f_in_selene_area:
		direction = global_position.direction_to(next_position)
		if global_position.distance_to(next_position) < 1:
			ind_move += 1
			if ind_move >= Global.player_trajectory.size():
				next_position = player.global_position
			else:
				next_position = Global.player_trajectory[ind_move]
		move(delta)
	else:
		Global.player_trajectory.clear()
		ind_move = 0
		idle(delta)
	move_and_slide()

func move(delta: float):
	anim_move()
	velocity = SPEED * direction * delta

func anim_move():
	if abs(direction[0]) < 0.5 and direction[1] > 0.5:
		anim.play("Down")
	elif abs(direction[0]) < 0.5 and direction[1] < -0.5:
		anim.play("Up")
	elif direction[0] < 0:
		anim.flip_h = true
		anim.play("Sides")
	else:
		anim.flip_h = false
		anim.play("Sides")

func idle(delta: float):
	velocity.x = 0
	velocity.y = 0
	anim.play("Idle")
	#if direction == D:
		#anim.play("Idle_down")
	#elif direction == U:
		#anim.play("Idle_up")
	#elif direction == L:
		#anim.flip_h = true
		#anim.play("Idle_sides")
	#else:
		#anim.flip_h = false
		#anim.play("Idle_sides")


func _on_area_2d_body_entered(body: Node2D) -> void:
	print("Внутри")
	f_in_selene_area = true

func _on_area_2d_body_exited(body: Node2D) -> void:
	print("Вышел")
	f_in_selene_area = false
	#next_position = player.global_position
