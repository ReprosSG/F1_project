{{config(
    materialized='external',
    location='azure://gold/drivers/gold_drivers_by_country.parquet'
)}}

WITH silver_data AS (
    SELECT *
    FROM 'azure://silver/drivers/silver_drivers.parquet'
)

SELECT code_pays, COUNT(numero_pilote) AS nombre_de_pilotes
FROM silver_data
WHERE code_pays IS NOT NULL
GROUP BY code_pays
ORDER BY nombre_de_pilotes DESC;