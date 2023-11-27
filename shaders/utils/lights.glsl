struct PointLight {
    vec3 position; // light position in view space
    vec3 Ia;    // ambient light properties
    vec3 Id;    // diffuse properties of the light source
    vec3 Is;    // specular properties of the light source

    float constant;
    float linear;
    float quadratic;
    float intensity;
};

struct SpotLight {
    vec3 position; // light position in view space
    vec3 direction; // light direction in view space
    vec3 Ia;    // ambient light properties
    vec3 Id;    // diffuse properties of the light source
    vec3 Is;    // specular properties of the light source

    float constant;
    float linear;
    float quadratic;
    float intensity;

    float cutoff;
    float outer_cutoff;
};

struct DirLight {
    vec3 dir;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

#define MAX_LIGHTS 6
#define MAX_SPOT_LIGHTS 3