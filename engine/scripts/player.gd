extends CharacterBody2D

const SPEED = 3500
enum {
	D,
	U,
	L,
	R,
	DR,
	DL,
	UR,
	UL
}

@onready var anim = $AnimatedSprite2D
var direction = D

func _physics_process(delta: float) -> void:
	var dir_x: int
	var dir_y: int
	if is_move():
		dir_x = obt_dir()[0]
		dir_y = obt_dir()[1]
		move(dir_x, dir_y, delta)
	else:
		idle(delta)
	move_and_slide()

func obt_dir() -> Array:
	var dir_x: int
	var dir_y: int
	if Input.is_action_pressed("up"):
		dir_y = -1
		direction = U
	elif Input.is_action_pressed("down"):
		dir_y = 1
		direction = D
	else:
		dir_y = 0
	if Input.is_action_pressed("right"):
		dir_x = 1
		if dir_y == 0:
			direction = R
		elif dir_y == 1:
			direction = DR
		else:
			direction = UR
	elif Input.is_action_pressed("left"):
		dir_x = -1
		if dir_y == 0:
			direction = L
		elif dir_y == 1:
			direction = DL
		else:
			direction = UL
	else:
		dir_x = 0
	return [dir_x, dir_y]

func is_move() -> bool:
	if Input.is_action_pressed("up") or Input.is_action_pressed("down") or Input.is_action_pressed("left") or Input.is_action_pressed("right"):
		return true
	else: 
		return false

func move(dir_x: int, dir_y: int, delta: float):
	if direction == D:
		anim.play("Down")
	elif direction == U:
		anim.play("Up")
	elif direction == L or direction == UL or direction == DL:
		anim.flip_h = true
		anim.play("Sides")
	else:
		anim.flip_h = false
		anim.play("Sides")
	velocity.x = SPEED * dir_x * delta
	velocity.y = SPEED * dir_y * delta
	
#func up_move(delta: float):
	#anim.play("Up")
	#velocity.x = 0
	#velocity.y = -SPEED * delta
	#direction = U
	#
#func down_move(delta: float):
	#anim.play("Down")
	#velocity.x = 0
	#velocity.y = SPEED * delta
	#direction = D
	#
#func left_move(delta: float):
	#anim.flip_h = true
	#anim.play("Sides")
	#velocity.x = -SPEED * delta
	#velocity.y = 0
	#direction = L
#
#func right_move(delta: float):
	#anim.flip_h = false
	#anim.play("Sides")
	#velocity.x = SPEED * delta
	#velocity.y = 0
	#direction = R
	
func idle(delta: float):
	velocity.x = 0
	velocity.y = 0
	if direction == D:
		anim.play("Idle_down")
	elif direction == U:
		anim.play("Idle_up")
	elif direction == L:
		anim.flip_h = true
		anim.play("Idle_sides")
	else:
		anim.flip_h = false
		anim.play("Idle_sides")
