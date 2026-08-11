shader_type canvas_item;

uniform float time;

void fragment() {
    vec2 uv = UV;
    
    // Волна ветра
    float wave = sin(uv.y * 20.0 + time * 2.0) * 0.02;
    uv.x += wave;
    
    COLOR = texture(TEXTURE, uv);
}
