# version 330 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;        // the fragment colour
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
    sampler2D textureObject; // texture object
    int has_texture;
};

struct Light {
    vec3 position; // light position in view space
    vec3 Ia;    // ambient light properties
    vec3 Id;    // diffuse properties of the light source
    vec3 Is;    // specular properties of the light source
};

#define MAX_LIGHTS 16

uniform Material material;
uniform Light lights[MAX_LIGHTS];
uniform int light_count;


///=== main shader code
// void main() {
//     // 1. calculate vectors used for shading calculations
//     vec3 camera_direction = -normalize(position_view_space);

//     vec4 combined = vec4(0.0f);

//     for (int i = 0; i < light_count; i++) {
//         Light l = lights[i];
//         vec3 light_direction = normalize(l.position-position_view_space);


//         // 2. now we calculate light components
//         vec4 ambient = vec4(l.Ia*material.Ka,material.alpha);
//         vec4 diffuse = vec4(l.Id*material.Kd*max(0.0f,dot(light_direction, normal_view_space)), material.alpha);
//         vec4 specular = vec4(l.Is*material.Ks*pow(max(0.0f, dot(reflect(light_direction, normal_view_space), -camera_direction)), material.Ns), material.alpha);

//         // 3. we calculate the attenuation function
//         // in this formula, dist should be the distance between the surface and the light
//         float dist = length(l.position - position_view_space);
//         float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);

//         combined += attenuation*(ambient + diffuse + specular);
//     }

//     // 4. we calculate the final colour
//     vec4 texColor = vec4(1.0);
//     if (material.has_texture == 1) {
//         texColor = texture(material.textureObject, fragment_texCoord);
//     }

//     final_color = combined*texColor;
// }

void main() {
    vec3 ambient = vec3(0.0);
    vec3 diffuse = vec3(0.0);
    vec3 specular = vec3(0.0);
    vec3 normal = normalize(normal_view_space);
    vec3 viewDir = normalize(-position_view_space);
    
    for (int i = 0; i < light_count; ++i) {
        vec3 lightDir = normalize(lights[i].position - position_view_space);
        float lambertian = max(dot(lightDir, normal), 0.0);
        vec3 reflectDir = reflect(-lightDir, normal);
        float spec = pow(max(dot(reflectDir, viewDir), 0.0), material.Ns);

        float dist = length(lights[i].position - position_view_space);
        float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);
        attenuation = 1.0;
        
        ambient += (lights[i].Ia * material.Ka) * attenuation;
        diffuse += (lambertian * lights[i].Id * material.Kd) *attenuation;
        specular += (spec * lights[i].Is * material.Ks) * attenuation;
    }
    
    vec3 finalColor = ambient + diffuse + specular;
    if (material.has_texture == 1) {
        vec4 texColor = texture(material.textureObject, fragment_texCoord);
        finalColor *= texColor.rgb;
    }
    
    final_color = vec4(finalColor, material.alpha);
}


