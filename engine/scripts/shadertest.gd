extends Sprite2D


func _ready() -> void:
	set_instance_shader_parameter("random12", randf_range(-5.0, 5.0))


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
 
