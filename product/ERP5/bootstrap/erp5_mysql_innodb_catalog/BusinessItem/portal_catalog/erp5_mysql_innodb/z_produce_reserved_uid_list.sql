INSERT INTO
  catalog (id, path)
VALUES
<dtml-in "_.range(count - 1)">
( <dtml-sqlvar instance_id type="string"> , 'reserved' ) ,
</dtml-in>
( <dtml-sqlvar instance_id type="string"> , 'reserved' );

<dtml-var "'\0'">

SELECT   
  uid
FROM 
  catalog 
WHERE
  path = 'reserved'
AND
  id = <dtml-sqlvar instance_id type="string">
LIMIT
  10000
