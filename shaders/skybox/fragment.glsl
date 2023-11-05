#version 330

in vec3 fragment_texCoord;
out vec4 final_color;

uniform samplerCube skybox_sampler;

void main(void)
{
	vec3 fragment_texCoord = fragment_texCoord;
	final_color = texture(skybox_sampler, fragment_texCoord);
}
