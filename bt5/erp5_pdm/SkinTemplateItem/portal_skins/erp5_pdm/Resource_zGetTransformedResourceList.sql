select distinct
  catalog.uid, catalog.relative_url, catalog.title
from
  transformation 
join 
  catalog on transformation.transformed_uid=catalog.uid

where
  <dtml-sqltest resource_uid column="transformation.uid" type=int multiple>