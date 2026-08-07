extends TileMapLayer


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	set_instance_shader_parameter("random12", randf_range(-10.0, 10.0))


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
