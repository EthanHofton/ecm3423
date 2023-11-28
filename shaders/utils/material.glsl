/**
 * @struct Material
 * @brief Represents the properties of a material used for shading.
 *
 * This struct will be received as a unifrom, so it contains sampler2D variables for each texture.
 *
 * The Material struct contains various properties such as ambient reflection, diffuse reflection,
 * specular reflection, specular exponent, alpha value, and texture maps for diffuse, specular,
 * roughness, and bump mapping. It also includes flags to indicate whether each texture map is used.
 */
struct Material {
    vec3 Ka;            // ambient reflection properties of the material
    vec3 Kd;            // diffuse reflection propoerties of the material
    vec3 Ks;            // specular properties of the material
    float Ns;           // specular exponent
    float alpha;        // alpha value of the material
    sampler2D map_Kd;   // diffuse map
    sampler2D map_Ks;   // specular map
    sampler2D map_Ns;   // roughness map
    sampler2D map_bump; // bump map

    int use_map_Kd;     // flag to indicate if diffuse map is used
    int use_map_Ks;     // flag to indicate if specular map is used
    int use_map_Ns;     // flag to indicate if roughness map is used
    int use_map_bump;   // flag to indicate if bump map is used
};

/**
 * @struct Mat
 * @brief Represents a material with reflection properties.
 *
 * This struct contains the ambient, diffuse, and specular reflection properties of a material,
 * as well as the specular exponent and alpha value.
 *
 * @var Ka The ambient reflection properties of the material.
 * @var Kd The diffuse reflection properties of the material.
 * @var Ks The specular properties of the material.
 * @var Ns The specular exponent.
 * @var alpha The alpha value of the material.
 */
struct Mat {
    vec3 Ka;     // ambient reflection properties of the material
    vec3 Kd;     // diffuse reflection properties of the material
    vec3 Ks;     // specular properties of the material
    float Ns;    // specular exponent
    float alpha; // alpha value of the material
};