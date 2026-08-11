extends CharacterBody2D

const SPEED = 3500

@onready var anim = $AnimPlayer
@onready var tilemap = $"../TileMapLayer/map/osnova"
var direction: Vector2 = Vector2(0, 0)
var speed_mult: float = 1.0

func _physics_process(delta: float) -> void:
	# Передвижение персонажа
	direction = Vector2(Input.get_axis("left", "right"), Input.get_axis("up", "down")).normalized()
	get_speed_multiplier()
	if is_move():
		move(delta)
	else:
		idle(delta)
	move_and_slide()
	speed_mult = 1.0
	# Сохранение позиции игрока
	Global.player_position = global_position

func get_speed_multiplier() -> void:
	var position = tilemap.local_to_map(global_position)
	var tile_data = tilemap.get_cell_tile_data(position)
	
	if tile_data and tile_data.get_custom_data("speed_multiplier"):
		print("Yes")
		speed_mult = speed_mult - tile_data.get_custom_data("speed_multiplier")
		print(speed_mult)
	#print(speed_mult)
func is_move() -> bool:
	if direction != Vector2(0, 0):
		return true
	else: 
		return false

func move(delta: float):
	anim_move()
	velocity = SPEED * direction * speed_mult * delta

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
