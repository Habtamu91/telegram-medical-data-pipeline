
    
    

select
    channel_id as unique_field,
    count(*) as n_records

from "telegram_medical"."telegram_raw"."channels"
where channel_id is not null
group by channel_id
having count(*) > 1


