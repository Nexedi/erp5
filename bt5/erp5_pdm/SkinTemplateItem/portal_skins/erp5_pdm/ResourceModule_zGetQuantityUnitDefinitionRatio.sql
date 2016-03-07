select quantity from quantity_unit_conversion
where 
  <dtml-sqltest resource_uid type="int"> and
  <dtml-sqltest quantity_unit_uid type="int">