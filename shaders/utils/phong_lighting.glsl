
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

vec3 point_light(PointLight l, Mat m, vec3 normal, vec3 viewDir, vec3 fragPos) {
    vec3 lightDir = normalize(l.position - fragPos);
    float lambertian = max(dot(lightDir, normal), 0.0);
    lambertian = clamp(lambertian, 0.0, 1.0);

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(reflectDir, viewDir), 0.0), m.Ns);
    spec = clamp(spec, 0.0, 1.0);

    float dist = length(l.position - fragPos);
    float attenuation = 1.0 / (l.constant + l.linear * dist + l.quadratic * (dist * dist));    
    attenuation *= l.intensity;
    attenuation = clamp(attenuation, 0.0, 1.0);
    
    vec3 ambient =  (l.Ia * m.Ka)              * attenuation;
    vec3 diffuse =  (l.Id * m.Kd * lambertian) * attenuation;
    vec3 specular = (l.Is * m.Ks * spec)       * attenuation;

    return ambient + diffuse + specular;
}

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