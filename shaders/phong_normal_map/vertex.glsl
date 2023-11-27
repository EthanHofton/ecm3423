//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec3 normal;		// store the vertex normal
in vec2 texCoord;
in vec3 tangent;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragPos;            // the position of the vertex in world space
out vec2 fragment_texCoord;  // the texture coordinates of the vertex
out mat3 TBN;                // the TBN matrix

//=== uniforms
uniform mat4 PVM; 	// the Perspective-View-Model matrix is received as a Uniform
uniform mat4 M;     // the Model matrix

void main() {
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);

    // 2. calculate vectors used for shading calculations
    // those will be interpolate before being sent to the
    // fragment shader.
    fragPos = vec3(M*vec4(position,1.0f));

    // calculater the TBN matrix (equation found from learnOpenGL.com)
    mat3 MiT = transpose(inverse(mat3(M)));
    vec3 N = normalize(MiT * normal);
    vec3 T = normalize(MiT * tangent);
    T = normalize(T - dot(T, N) * N);
    // then retrieve perpendicular vector B with the cross product of T and N
    vec3 B = cross(N, T);

    TBN = mat3(T, B, N);

    // 3. forward the texture coordinates.
    fragment_texCoord = texCoord;
}
