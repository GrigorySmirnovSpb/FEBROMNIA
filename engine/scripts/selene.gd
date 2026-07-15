extends CharacterBody2D

const SPEED = 3000
@onready var anim = $AnimSelene

var direction: Vector2 = Vector2(0, 0)

func _physics_process(delta: float) -> void:
	if global_position.distance_to(Global.player_position) > 20:
		direction = global_position.direction_to(Global.player_position)
		move(delta)
	else:
		idle(delta)
	move_and_slide()
func move(delta: float):
	print(direction)
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
