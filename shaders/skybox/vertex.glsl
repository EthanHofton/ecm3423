//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragment_texCoord;

uniform mat4 PVM;

void main(void)
{
	gl_Position = PVM*vec4(position, 1);
	fragment_texCoord = position;
}
