SELECT *
FROM {{ ref('silver_drivers') }}
WHERE trim(nom_pilote) = ''
