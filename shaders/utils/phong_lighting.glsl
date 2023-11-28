
/**
 * Calculates the Phong lighting model for a directional light source.
 *
 * @param l The directional light source.
 * @param m The material properties.
 * @param normal The surface normal.
 * @param viewDir The direction of the viewer.
 * @return The resulting color after applying the Phong lighting model.
 */
vec3 directional_light(DirLight l, Mat m, vec3 normal, vec3 viewDir) {
    // Calculate the direction of the light source
    vec3 lightDir = normalize(-l.dir);

    // Calculate the Lambertian term
    float lambertian = max(dot(lightDir, normal), 0.0);
    lambertian = clamp(lambertian, 0.0, 1.0);

    // Calculate the specular term
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(reflectDir, viewDir), 0.0), m.Ns);
    spec = clamp(spec, 0.0, 1.0);

    // Calculate the ambient, diffuse, and specular components
    vec3 ambient =  (l.Ia * m.Ka);
    vec3 diffuse =  (l.Id * m.Kd * lambertian);
    vec3 specular = (l.Is * m.Ks * spec);

    // Combine the components to get the final color
    return ambient + diffuse + specular;
}

/**
 * Calculates the Phong lighting model for a point light source.
 *
 * @param l         The point light source.
 * @param m         The material properties.
 * @param normal    The surface normal.
 * @param viewDir   The direction from the fragment to the viewer.
 * @param fragPos   The position of the fragment.
 * @return          The resulting color from the Phong lighting model.
 */
vec3 point_light(PointLight l, Mat m, vec3 normal, vec3 viewDir, vec3 fragPos) {
    // Calculate the direction from the fragment to the light source
    vec3 lightDir = normalize(l.position - fragPos);

    // Calculate the Lambertian term
    float lambertian = max(dot(lightDir, normal), 0.0);
    lambertian = clamp(lambertian, 0.0, 1.0);

    // Calculate the specular term
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(reflectDir, viewDir), 0.0), m.Ns);
    spec = clamp(spec, 0.0, 1.0);

    // Calculate the distance between the light source and the fragment
    float dist = length(l.position - fragPos);

    // Calculate the attenuation factor based on the distance
    float attenuation = 1.0 / (l.constant + l.linear * dist + l.quadratic * (dist * dist));
    attenuation *= l.intensity;
    attenuation = clamp(attenuation, 0.0, 1.0);

    // Calculate the ambient, diffuse, and specular components
    vec3 ambient =  (l.Ia * m.Ka)              * attenuation;
    vec3 diffuse =  (l.Id * m.Kd * lambertian) * attenuation;
    vec3 specular = (l.Is * m.Ks * spec)       * attenuation;

    // Combine the components to get the final color
    return ambient + diffuse + specular;
}

/**
 * Calculates the lighting contribution from a spot light source with smooth edges.
 *
 * @param l         The spot light source.
 * @param m         The material properties.
 * @param normal    The surface normal at the fragment position.
 * @param viewDir   The direction from the fragment position to the viewer.
 * @param fragPos   The position of the fragment in world space.
 * @return          The final color contribution from the spot light.
 */
vec3 spot_light_smooth(SpotLight l, Mat m, vec3 normal, vec3 viewDir, vec3 fragPos) {
    // lighting calc same as point light
    vec3 lightDir = normalize(l.position - fragPos);
    float lambertian = max(dot(lightDir, normal), 0.0);
    lambertian = clamp(lambertian, 0.0, 1.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(reflectDir, viewDir), 0.0), m.Ns);
    spec = clamp(spec, 0.0, 1.0);

    // spot light with soft edges
    float theta = dot(lightDir, normalize(-l.direction));
    float epsilon = l.cutoff - l.outer_cutoff;
    float intensity = clamp((theta - l.outer_cutoff) / epsilon, 0.0, 1.0);

    // attenuation
    float dist = length(l.position - fragPos);
    float attenuation = 1.0 / (l.constant + l.linear * dist + l.quadratic * (dist * dist));    
    attenuation *= l.intensity;
    attenuation = clamp(attenuation, 0.0, 1.0);
    
    // final color
    vec3 ambient =  (l.Ia * m.Ka)              * attenuation;
    vec3 diffuse =  (l.Id * m.Kd * lambertian) * attenuation;
    vec3 specular = (l.Is * m.Ks * spec)       * attenuation;

    return ambient + (diffuse * intensity) + (specular * intensity);
}

/**
 * Calculates the Phong lighting model for a spot light with hard edges.
 *
 * @param l         The spot light parameters (position, direction, cutoff, intensity)
 * @param m         The material parameters (ambient, diffuse, specular, shininess)
 * @param normal    The surface normal at the fragment position
 * @param viewDir   The direction from the fragment position to the viewer
 * @param fragPos   The position of the fragment in world space
 * @return          The final color of the fragment based on the Phong lighting model
 */
vec3 spot_light_hard(SpotLight l, Mat m, vec3 normal, vec3 viewDir, vec3 fragPos) {
    // lighting calc same as point light
    vec3 lightDir = normalize(l.position - fragPos);
    
    // attenuation
    float dist = length(l.position - fragPos);
    float attenuation = 1.0 / (l.constant + l.linear * dist + l.quadratic * (dist * dist));    
    attenuation *= l.intensity;
    attenuation = clamp(attenuation, 0.0, 1.0);

    // spot light with hard edges
    float theta = dot(lightDir, normalize(-l.direction));
    if (theta < l.cutoff) {
        return (l.Ia * m.Ka) * attenuation;
    }

    // lighting calc same as point light
    float lambertian = max(dot(lightDir, normal), 0.0);
    lambertian = clamp(lambertian, 0.0, 1.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(reflectDir, viewDir), 0.0), m.Ns);
    spec = clamp(spec, 0.0, 1.0);

    // attenuation
    
    // final color
    vec3 ambient =  (l.Ia * m.Ka)              * attenuation;
    vec3 diffuse =  (l.Id * m.Kd * lambertian) * attenuation;
    vec3 specular = (l.Is * m.Ks * spec)       * attenuation;

    return ambient + diffuse + specular;
}