//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragPos; // position of the fragment in world space
in vec2 fragment_texCoord; // texture coordinates of the fragment
in mat3 TBN; // tangent, bitangent, normal matrix

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec4 final_color;

//=== includes
#include "utils/material.glsl"
#include "utils/lights.glsl"
#include "utils/phong_lighting.glsl"

//=== uniform variables
uniform Material material; // material properties

uniform PointLight lights[MAX_LIGHTS]; // point lights
uniform int light_count; // number of point lights

uniform SpotLight spot_lights[MAX_SPOT_LIGHTS]; // spot lights
uniform int spot_light_count; // number of spot lights

uniform DirLight dir_light; // directional light

uniform vec3 viewPos; // position of the camera in world space

void main() {
    vec3 normal = texture(material.map_bump, fragment_texCoord).rgb;
    normal = normal * 2.0 - 1.0;
    normal = normalize(TBN * normal);

    vec3 viewDir = normalize(viewPos - fragPos);

    Mat m;
    m.Ka = material.Ka;
    m.Kd = material.Kd;
    m.Ks = material.Ks;
    m.Ns = material.Ns;
    m.alpha = material.alpha;

    if (material.use_map_Kd == 1) {
        m.Kd = texture(material.map_Kd, fragment_texCoord).rgb;
        m.Ka = texture(material.map_Kd, fragment_texCoord).rgb;
    }

    if (material.use_map_Ks == 1) {
        m.Ks = texture(material.map_Ks, fragment_texCoord).rgb;
    }

    if (material.use_map_Ns == 1) {
        m.Ns = texture(material.map_Ns, fragment_texCoord).r;
    }

    vec3 finalColor = directional_light(dir_light, m, normal, viewDir);

    for (int i = 0; i < light_count; ++i) {
        finalColor += point_light(lights[i], m, normal, viewDir, fragPos);
    }

    for (int i = 0; i < spot_light_count; ++i) {
        finalColor += spot_light_smooth(spot_lights[i], m, normal, viewDir, fragPos);
    }
    
    final_color = vec4(finalColor, material.alpha);
}