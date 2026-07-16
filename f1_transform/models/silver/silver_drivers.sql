{{ config(
    materialized='external',
    location='azure://silver/drivers/silver_drivers.parquet'
) }}

WITH source_data AS (
    SELECT *
    FROM {{ source('bronze_sources', 'drivers_latest') }}
)

SELECT
    CAST(driverId AS VARCHAR) AS id_pilote,
    TRY_CAST(permanentNumber AS INTEGER) AS numero_pilote,
    CAST(givenName AS VARCHAR) AS prenom,
    UPPER(CAST(familyName AS VARCHAR)) AS nom_pilote,
    CAST(code AS VARCHAR) AS acronyme,
    TRY_CAST(dateOfBirth AS DATE) AS date_naissance,
    COALESCE(CAST(nationality AS VARCHAR), 'Non renseignee') AS nationalite
FROM source_data
WHERE driverID IS NOT NULL
