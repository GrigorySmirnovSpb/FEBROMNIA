extends TileMapLayer

func _ready():
	material.set_shader_parameter("time", 0.0)

func _process(delta):
	var t = material.get_shader_parameter("time") + delta
	material.set_shader_parameter("time", t)
