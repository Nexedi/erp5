SELECT
  DISTINCT(third_party) AS title,
  CONCAT('<dtml-var getPath>/organisation_module/', third_party) AS path,
  CONCAT('Organisation ', third_party) AS gid
FROM
  NOMACTX
WHERE
  <dtml-if id>
    <dtml-sqltest id op="eq" column="third_party" type="string">
    AND
  </dtml-if>
  third_party <> account_code
ORDER BY third_party ASC