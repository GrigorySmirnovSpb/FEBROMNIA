extends CharacterBody2D

const SPEED = 3500
const speed_mult: float = 1.0

@onready var anim = $AnimPlayer
@onready var tilemap = $"../TileMapLayer/map/osnova"

var direction: Vector2 = Vector2.ZERO
var last_direction: Vector2 = Vector2.ZERO

func _ready() -> void:
	pass

func _physics_process(delta: float) -> void:
	# Передвижение персонажа
	direction = Vector2(Input.get_axis("left", "right"), Input.get_axis("up", "down")).normalized()
	var speed_multiplier = get_speed_multiplier()
	if is_move():
		move(speed_multiplier, delta)
	else:
		idle(delta)
	move_and_slide()
	
	if last_direction != direction:
		Global.player_trajectory.append(global_position)
		if Global.player_trajectory.size() > 100:
			Global.player_trajectory.pop_front()
	last_direction = direction
	Global.player_position = global_position

func get_speed_multiplier() -> float:
	var local_pos = tilemap.to_local(global_position + Vector2(0, 10))
	var tile_pos = tilemap.local_to_map(local_pos)
	var tile_data = tilemap.get_cell_tile_data(tile_pos)
	
	if tile_data:
		return speed_mult - tile_data.get_custom_data("speed_multiplier")
	else:
		return speed_mult

func is_move() -> bool:
	if direction != Vector2(0, 0):
		return true
	else: 
		return false

func move(speed_multiplier: float, delta: float):
	anim_move()
	velocity = SPEED * direction * speed_multiplier * delta

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

func idle(delta: float): # Это просто стояне на месте
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
