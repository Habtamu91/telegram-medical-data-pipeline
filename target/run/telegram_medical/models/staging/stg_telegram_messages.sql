
  create view "telegram_medical"."public"."stg_messages__dbt_tmp"
    
    
  as (
    

SELECT
    message_id::VARCHAR(255) AS message_key,
    channel_id::VARCHAR(255) AS channel_key,
    message_text::TEXT AS message_content,
    -- Extract date/time components
    DATE(message_date) AS message_date,
    EXTRACT(HOUR FROM message_date) AS message_hour,
    -- Flags
    CASE WHEN media_url IS NOT NULL THEN TRUE ELSE FALSE END AS has_media,
    -- Metadata
    'telegram' AS source_system,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM "telegram_medical"."telegram_raw"."messages"
WHERE message_date >= '2025-01-01'  -- Filter for recent data
  );