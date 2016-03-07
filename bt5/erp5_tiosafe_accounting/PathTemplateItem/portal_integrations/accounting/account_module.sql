SELECT
  DISTINCT(account_code) AS identifier,
  CONCAT('Reference/', account_code) AS category,
  account_name AS title,
  CONCAT('<dtml-var getPath>/account_module/', account_code) AS path,
  CONCAT('Account ', account_code) AS gid
FROM
  NOMACTX
<dtml-if id>
WHERE
  <dtml-sqltest id op="eq" column="account_code" type="int">
</dtml-if>
ORDER BY account_code ASC