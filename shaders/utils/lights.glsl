/**
 * @struct PointLight
 * @brief Represents a point light source in the scene.
 *
 * @var position Light position in world space.
 * @var Ia Ambient light properties.
 * @var Id Diffuse properties of the light source.
 * @var Is Specular properties of the light source.
 * @var constant Attenuation constant.
 * @var linear Attenuation linear.
 * @var quadratic Attenuation quadratic.
 * @var intensity Light intensity.
 */
struct PointLight {
    vec3 position;   // light position in world space
    vec3 Ia;         // ambient light properties
    vec3 Id;         // diffuse properties of the light source
    vec3 Is;         // specular properties of the light source

    float constant;  // attenuation constant
    float linear;    // attenuation linear
    float quadratic; // attenuation quadratic
    float intensity; // light intensity
};

/**
 * @struct SpotLight
 * @brief Represents a spot light source in the scene.
 *
 * @var position Light position in world space.
 * @var direction Light direction in world space.
 * @var Ia Ambient light properties.
 * @var Id Diffuse properties of the light source.
 * @var Is Specular properties of the light source.
 * @var constant Attenuation constant.
 * @var linear Attenuation linear.
 * @var quadratic Attenuation quadratic.
 * @var intensity Light intensity.
 * @var cutoff Cutoff angle cosine.
 * @var outer_cutoff Outer cutoff angle cosine.
 */
struct SpotLight {
    vec3 position;   // light position in world space
    vec3 direction;  // light direction in world space
    vec3 Ia;         // ambient light properties
    vec3 Id;         // diffuse properties of the light source
    vec3 Is;         // specular properties of the light source

    float constant;  // attenuation constant
    float linear;    // attenuation linear
    float quadratic; // attenuation quadratic
    float intensity; // light intensity

    float cutoff;       // cutoff angle cosine
    float outer_cutoff; // outer cutoff angle cosine
};

/**
 * @struct DirLight
 * @brief Represents a directional light source in the scene.
 *
 * @var dir Light direction in world space.
 * @var Ia Ambient light properties.
 * @var Id Diffuse properties of the light source.
 * @var Is Specular properties of the light source.
 */
struct DirLight {
    vec3 dir;  // light direction in world space
    vec3 Ia;   // ambient light properties
    vec3 Id;   // diffuse properties of the light source
    vec3 Is;   // specular properties of the light source
};

// max number of point lights
// #define MAX_LIGHTS 6
#define MAX_LIGHTS 30
// max number of spot lights
#define MAX_SPOT_LIGHTS 3
