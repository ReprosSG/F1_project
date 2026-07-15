SELECT *
FROM {{ ref('silver_drivers') }}
WHERE trim(nom_complet) = '' OR trim(nom_pilote) = ''
