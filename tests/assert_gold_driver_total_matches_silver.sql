WITH silver_total AS (
    SELECT count(*) AS total
    FROM {{ ref('silver_drivers') }}
    WHERE nationalite IS NOT NULL
      AND trim(nationalite) <> ''
),

gold_total AS (
    SELECT coalesce(sum(nombre_pilotes), 0) AS total
    FROM {{ ref('gold_drivers_by_country') }}
)

SELECT
    silver_total.total AS total_silver,
    gold_total.total AS total_gold
FROM silver_total
CROSS JOIN gold_total
WHERE silver_total.total <> gold_total.total