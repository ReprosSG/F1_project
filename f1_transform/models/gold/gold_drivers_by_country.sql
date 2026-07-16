{{config(
    materialized='external',
    location='azure://gold/drivers/gold_drivers_by_country.parquet'
)}}

WITH silver_data AS (
    SELECT *
    FROM {{ ref('silver_drivers') }}
)

SELECT 
    nationalite, 
    COUNT(id_pilote) AS nombre_de_pilotes
FROM silver_data
WHERE nationalite IS NOT NULL
GROUP BY nationalite
ORDER BY nombre_de_pilotes DESC