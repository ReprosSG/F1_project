{{ config(
    materialized='external',
    location='azure://silver/drivers/silver_drivers.parquet'
) }}

WITH source_data AS (
    SELECT *
    FROM 'azure://bronze/drivers/drivers_latest.parquet'
)

SELECT
    TRY_CAST(driver_number AS INTEGER) AS numero_pilote,
    CAST(full_name AS VARCHAR) AS nom_complet,
    TRY_CAST(country_code AS INTEGER) AS code_pays,
    UPPER(last_name) AS nom_pilote
FROM source_data
WHERE driver_number IS NOT NULL
