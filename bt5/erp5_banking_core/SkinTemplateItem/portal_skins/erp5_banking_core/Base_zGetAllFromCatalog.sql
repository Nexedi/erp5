select 
  uid, relative_url, portal_type, simulation_state, source_reference
FROM catalog
WHERE 
  1=1
AND 
uid in (<dtml-in uid_list><dtml-sqlvar sequence-item type="string"><dtml-if sequence-end><dtml-else>, </dtml-if></dtml-in>)