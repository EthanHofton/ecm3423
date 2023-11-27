in vec3 fragPos;   // the position of the vertex in view coordinates
in vec3 normal_world_space;     // the normal of the vertex in view coordinates

out vec4 final_color;

uniform vec3 viewPos;

uniform samplerCube env_map;

uniform float refractive_ratio;

void main(void)
{
    vec3 I = normalize(fragPos- viewPos);
    vec3 R = refract(I, normalize(normal_world_space), refractive_ratio);
	final_color = vec4(texture(env_map, R).rgb, 1);
}
