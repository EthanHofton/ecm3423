#version 330 // required to use OpenGL core standard

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec4 final_color;
in vec2 o_texCoord;
uniform sampler2D test_texture_sampler;
uniform int has_texture;

void main() {
    final_color = texture(test_texture_sampler, o_texCoord) * vec4(1.0f);
}


