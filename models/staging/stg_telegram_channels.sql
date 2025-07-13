{{
  config(
    materialized='table',
    alias='stg_channels'
  )
}}

SELECT
    channel_id::VARCHAR(255) AS channel_key,
    channel_name::VARCHAR(255) AS channel_name,
    subscriber_count::INTEGER AS subscribers,
    is_verified::BOOLEAN AS is_verified,
    'telegram' AS source_system,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ source('telegram_raw', 'channels') }}