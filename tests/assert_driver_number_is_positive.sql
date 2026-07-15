SELECT *
FROM {{ ref('silver_drivers') }}
WHERE numero_pilote <= 0
