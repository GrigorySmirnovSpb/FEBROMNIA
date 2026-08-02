extends Area2D

@onready var Text = $Label

var f_in = false

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	Text.visible = false


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if f_in && Input.is_action_pressed("action"):
		Text.text = "Ты пидорас"


func _on_body_entered(body: Node2D) -> void:
	f_in = true
	Text.visible = true

func _on_body_exited(body: Node2D) -> void:
	f_in = false
	Text.visible = false
