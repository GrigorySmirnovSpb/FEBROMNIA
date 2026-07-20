extends CharacterBody2D

const SPEED = 3500

@onready var anim = $AnimPlayer
var direction: Vector2 = Vector2(0, 0)

func _physics_process(delta: float) -> void:
	# Передвижение персонажа
	direction = Vector2(Input.get_axis("left", "right"), Input.get_axis("up", "down")).normalized()
	if is_move():
		move(delta)
	else:
		idle(delta)
	move_and_slide()

func is_move() -> bool:
	if direction != Vector2(0, 0):
		return true
	else: 
		return false

func move(delta: float):
	anim_move()
	velocity = SPEED * direction * delta

func anim_move():
	if direction == Vector2(0, 1):
		anim.play("Down")
	elif direction == Vector2(0, -1):
		anim.play("Up")
	elif direction[0] < 0:
		anim.flip_h = true
		anim.play("Sides")
	else:
		anim.flip_h = false
		anim.play("Sides")

# Это просто стояне на месте
func idle(delta: float):
	velocity.x = 0
	velocity.y = 0
	anim.play("Idle_down")
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
