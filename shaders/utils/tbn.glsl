/**
 * Calculates the TBN matrix (Tangent, Bitangent, Normal) based on the given normal and tangent vectors.
 *
 * @param normal The normal vector.
 * @param tangent The tangent vector.
 * @return The TBN matrix.
 */
mat3 calc_TBN(vec3 normal, vec3 tangent, mat3 MiT) {
    // transform normal and tangent to world space
    vec3 N = normalize(MiT * normal);
    vec3 T = normalize(MiT * tangent);
    // minor optimization
    T = normalize(T - dot(T, N) * N);
    // then retrieve perpendicular vector B with the cross product of T and N
    vec3 B = cross(N, T);

    return mat3(T, B, N);
}
