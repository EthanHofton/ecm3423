# version 330 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 position_view_space;   // the position in view coordinates of this fragment
in vec3 normal_view_space;     // the normal in view coordinates to this fragment
in vec2 fragment_texCoord;

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec4 final_color;

//=== uniforms
struct Material {
    vec3 Ka;    // ambient reflection properties of the material
    vec3 Kd;    // diffuse reflection propoerties of the material
    vec3 Ks;    // specular properties of the material
    float Ns;   // specular exponent
    float alpha; // alpha value of the material
    sampler2D map_Kd;
    sampler2D map_Ks;

    int use_map_Kd;
    int use_map_Ks;
};

struct Light {
    vec3 position; // light position in view space
    vec3 Ia;    // ambient light properties
    vec3 Id;    // diffuse properties of the light source
    vec3 Is;    // specular properties of the light source
};

#define MAX_LIGHTS 6

uniform Material material;
uniform Light lights[MAX_LIGHTS];
uniform int light_count;

void main() {
    vec3 ambient = vec3(0.0);
    vec3 diffuse = vec3(0.0);
    vec3 specular = vec3(0.0);
    vec3 normal = normalize(normal_view_space);
    vec3 viewDir = normalize(-position_view_space);

    vec3 kA = material.Ka;
    vec3 kD = material.Kd;
    vec3 kS = material.Ks;

    if (material.use_map_Kd == 1) {
        kD = texture(material.map_Kd, fragment_texCoord).rgb;
    }

    if (material.use_map_Ks == 1) {
        kS = texture(material.map_Ks, fragment_texCoord).rgb;
    }

    for (int i = 0; i < light_count; ++i) {
        vec3 lightDir = normalize(lights[i].position - position_view_space);
        float lambertian = max(dot(lightDir, normal), 0.0);
        vec3 reflectDir = reflect(-lightDir, normal);
        float spec = pow(max(dot(reflectDir, viewDir), 0.0), material.Ns);

        float dist = length(lights[i].position - position_view_space);
        float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);
        attenuation = 1.0;
        
        ambient += (lights[i].Ia * kA) * attenuation;
        diffuse += (lambertian * lights[i].Id * kD) *attenuation;
        specular += (spec * lights[i].Is * kS) * attenuation;
    }
    
    vec3 finalColor = ambient + diffuse + specular;
    final_color = vec4(finalColor, material.alpha);
}