//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec3 normal;		// store the vertex normal

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragPos;   // the position of the vertex in view coordinates
out vec3 normal_world_space;     // the normal of the vertex in view coordinates


uniform mat4 PVM; 	// the Perspective-View-Model matrix is received as a Uniform
uniform mat4 M;

void main(void)
{
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);

    mat3 MiT = transpose(inverse(mat3(M)));

    // 2. calculate vectors used for shading calculations
    // those will be interpolate before being sent to the
    // fragment shader.
    normal_world_space = normalize(MiT * normal);
    fragPos = vec3(M*vec4(position,1.0f));
}