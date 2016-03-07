select transformation.quantity from transformation
where
<dtml-sqltest uid type="int">
and <dtml-sqltest variation_text type="string">
and <dtml-sqltest transformed_uid type="int">
and <dtml-sqltest transformed_variation_text type="string">