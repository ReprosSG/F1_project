SELECT *
FROM {{ ref('silver_drivers') }}
WHERE nom_pilote <> upper(nom_pilote)