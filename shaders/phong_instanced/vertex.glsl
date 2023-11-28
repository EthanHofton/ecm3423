//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec3 normal;		// store the vertex normal
in vec2 texCoord;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragPos;            // the position of the vertex in world space
out vec2 fragment_texCoord;  // the texture coordinates of the vertex
out vec3 normal_world_space; // the normal of the vertex in world space

//=== uniforms
uniform mat4 M;
uniform mat4 PV;

uniform vec3 offsets[100];

void main() {
    vec3 offset = offsets[gl_InstanceID];
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    mat4 M_offset = mat4(1.0f);
    M_offset[3] = vec4(offset, 1.0f);
    mat4 M_combined = M_offset*M;

    mat4 PVM = PV*M_combined;
    gl_Position = PVM*vec4(position,1.0f);

    mat3 MiT = transpose(inverse(mat3(M_combined)));

    // 2. calculate vectors used for shading calculations
    // those will be interpolate before being sent to the
    // fragment shader.
    fragPos = vec3(M_combined*vec4(position,1.0f));
    
    // forwards the normal in world space
    normal_world_space = normalize(MiT*normal);

    // 3. forward the texture coordinates.
    fragment_texCoord = texCoord;
}
