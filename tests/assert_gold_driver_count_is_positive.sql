SELECT *
FROM {{ ref('gold_drivers_by_country') }}
WHERE nombre_pilotes <= 0