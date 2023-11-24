#version 330		// required to use OpenGL core standard

//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec3 normal;		// store the vertex normal
in vec2 texCoord;
in vec3 tangent;
in vec3 bitangent;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 position_view_space;   // the position of the vertex in view coordinates
out vec2 fragment_texCoord;
out vec3 viewPos_view_space;    // the position of the camera in view coordinates
out mat3 TBN;

//=== uniforms
uniform mat4 PVM; 	// the Perspective-View-Model matrix is received as a Uniform
uniform mat4 VM; 	// the View-Model matrix is received as a Uniform
uniform mat3 VMiT;  // The inverse-transpose of the view model matrix, used for normals
uniform vec3 viewPos; // The position of the camera in view space

void main() {
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);

    // 2. calculate vectors used for shading calculations
    // those will be interpolate before being sent to the
    // fragment shader.
    position_view_space = vec3(VM*vec4(position,1.0f));

    vec3 N = normalize(VMiT * normal);
    vec3 T = normalize(VMiT * tangent);
    // re-orthogonalize T with respect to N
    T = normalize(T - dot(T, N) * N);
    // then retrieve perpendicular vector B with the cross product of T and N
    vec3 B = cross(N, T);

    TBN = mat3(T, B, N);

    // 3. forward the texture coordinates.
    fragment_texCoord = texCoord;

    // 4. forward the view position in view space
    viewPos_view_space = viewPos;
}
