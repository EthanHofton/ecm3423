struct Material {
    vec3 Ka;    // ambient reflection properties of the material
    vec3 Kd;    // diffuse reflection propoerties of the material
    vec3 Ks;    // specular properties of the material
    float Ns;   // specular exponent
    float alpha; // alpha value of the material
    sampler2D map_Kd; // diffuse map
    sampler2D map_Ks; // specular map
    sampler2D map_Ns; // roughness map
    sampler2D map_bump; // bump map

    int use_map_Kd;
    int use_map_Ks;
    int use_map_Ns;
    int use_map_bump;
};

struct Mat {
    vec3 Ka;    // ambient reflection properties of the material
    vec3 Kd;    // diffuse reflection propoerties of the material
    vec3 Ks;    // specular properties of the material
    float Ns;   // specular exponent
    float alpha; // alpha value of the material
};