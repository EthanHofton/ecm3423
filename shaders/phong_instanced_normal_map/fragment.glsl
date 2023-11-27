# version 330 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 position_view_space;   // the position in view coordinates of this fragment
in mat3 TBN;                   // the TBN matrix for this fragment
in vec2 fragment_texCoord;
in vec3 viewPos_view_space;    // the position of the camera in view coordinates

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
    sampler2D map_Ns;
    sampler2D map_bump;

    int use_map_Kd;
    int use_map_Ks;
    int use_map_Ns;
};

struct Mat {
    vec3 Ka;    // ambient reflection properties of the material
    vec3 Kd;    // diffuse reflection propoerties of the material
    vec3 Ks;    // specular properties of the material
    float Ns;   // specular exponent
    float alpha; // alpha value of the material
};

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

uniform Material material;

uniform PointLight lights[MAX_LIGHTS];
uniform int light_count;

uniform SpotLight spot_lights[MAX_SPOT_LIGHTS];
uniform int spot_light_count;

uniform DirLight dir_light;

vec3 directional_light(DirLight l, Mat m, vec3 normal, vec3 viewDir) {
    vec3 lightDir = normalize(-l.dir);
    float lambertian = max(dot(lightDir, normal), 0.0);
    lambertian = clamp(lambertian, 0.0, 1.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(reflectDir, viewDir), 0.0), m.Ns);
    spec = clamp(spec, 0.0, 1.0);

    vec3 ambient =  (l.Ia * m.Ka);
    vec3 diffuse =  (l.Id * m.Kd * lambertian);
    vec3 specular = (l.Is * m.Ks * spec);

    return ambient + diffuse + specular;
}

vec3 point_light(PointLight l, Mat m, vec3 normal, vec3 viewDir, vec3 position_view_space) {
    vec3 lightDir = normalize(l.position - position_view_space);
    float lambertian = max(dot(lightDir, normal), 0.0);
    lambertian = clamp(lambertian, 0.0, 1.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(reflectDir, viewDir), 0.0), material.Ns);
    spec = clamp(spec, 0.0, 1.0);

    float dist = length(l.position - position_view_space);
    float attenuation = 1.0 / (l.constant + l.linear * dist + l.quadratic * (dist * dist));    
    attenuation *= l.intensity;
    attenuation = clamp(attenuation, 0.0, 1.0);
    
    vec3 ambient =  (l.Ia * m.Ka)              * attenuation;
    vec3 diffuse =  (l.Id * m.Kd * lambertian) * attenuation;
    vec3 specular = (l.Is * m.Ks * spec)       * attenuation;

    return ambient + diffuse + specular;
}

vec3 spot_light(SpotLight l, Mat m, vec3 normal, vec3 viewDir, vec3 position_view_space) {
    // lighting calc same as point light
    vec3 lightDir = normalize(l.position - position_view_space);
    float lambertian = max(dot(lightDir, normal), 0.0);
    lambertian = clamp(lambertian, 0.0, 1.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(reflectDir, viewDir), 0.0), material.Ns);
    spec = clamp(spec, 0.0, 1.0);

    // spot light with soft edges
    float theta = dot(lightDir, normalize(-l.direction));
    float epsilon = l.cutoff - l.outer_cutoff;
    float intensity = clamp((theta - l.outer_cutoff) / epsilon, 0.0, 1.0);

    // attenuation
    float dist = length(l.position - position_view_space);
    float attenuation = 1.0 / (l.constant + l.linear * dist + l.quadratic * (dist * dist));    
    attenuation *= l.intensity;
    attenuation = clamp(attenuation, 0.0, 1.0);
    attenuation = 1;
    
    // final color
    vec3 ambient =  (l.Ia * m.Ka)              * attenuation;
    vec3 diffuse =  (l.Id * m.Kd * lambertian) * attenuation;
    vec3 specular = (l.Is * m.Ks * spec)       * attenuation;

    return ambient + diffuse * intensity + specular * intensity;
}

void main() {
    vec3 normal = texture(material.map_bump, fragment_texCoord).rgb;
    normal = normal * 2.0 - 1.0;
    normal = normalize(TBN * normal);    

    vec3 viewDir = normalize(viewPos_view_space - position_view_space);

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
        finalColor += point_light(lights[i], m, normal, viewDir, position_view_space);
    }
    
    for (int i = 0; i < spot_light_count; ++i) {
        finalColor += spot_light(spot_lights[i], m, normal, viewDir, position_view_space);
    }

    final_color = vec4(finalColor, material.alpha);
}