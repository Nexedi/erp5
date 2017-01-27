INSERT INTO
  catalog (id, path)
VALUES
<dtml-in "_.range(count - 1)">
( <dtml-sqlvar instance_id type="string"> , 'reserved' ) ,
</dtml-in>
<<<<<<< HEAD
( <dtml-sqlvar instance_id type="string"> , 'reserved' )

<dtml-var sql_delimiter>
=======
( <dtml-sqlvar instance_id type="string"> , 'reserved' );

<dtml-var "'\0'">
>>>>>>> 3ce2fc0... bt5_prototype: Move erp5_mysql_innodb_catalog back to BT5 type

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
