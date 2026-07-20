extends CharacterBody2D

const SPEED = 3000

@export var player: Node2D

@onready var anim = $AnimSelene
@onready var nav_agent = $NavigationAgent2D

var direction: Vector2 = Vector2(0, 0)

func _ready() -> void:
	nav_agent.path_desired_distance = 200.0
	nav_agent.target_desired_distance = 30.0
	nav_agent.path_max_distance = 200.0

func set_movement_target() -> void:
	await get_tree().physics_frame
	nav_agent.target_position = player.global_position

func _physics_process(delta: float) -> void:
	direction = to_local(nav_agent.get_next_path_position()).normalized()
	set_movement_target()
	if not nav_agent.is_target_reached():
		if direction != Vector2.ZERO:
			move(delta)
	else:
		idle()
	move_and_slide()

func move(delta: float):
	print(direction)
	anim_move()
	velocity = SPEED * direction * delta

func anim_move():
	if abs(direction[0]) <= 0.5 and direction[1] >= 0.5:
		anim.play("Down")
	elif abs(direction[0]) <= 0.5 and direction[1] <= -0.5:
		anim.play("Up")
	elif direction[0] < 0:
		anim.flip_h = true
		anim.play("Sides")
	else:
		anim.flip_h = false
		anim.play("Sides")

func idle():
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
