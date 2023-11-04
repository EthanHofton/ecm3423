#version 330		// required to use OpenGL core standard

//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec2 texCoord;	// the texcoord attribute contains the vertex texture coordinates

//=== uniforms
uniform mat4 PVM; 	// the Perspective-View-Model matrix is received as a Uniform

out vec2 o_texCoord;

void main() {
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);
    o_texCoord = texCoord;
}
