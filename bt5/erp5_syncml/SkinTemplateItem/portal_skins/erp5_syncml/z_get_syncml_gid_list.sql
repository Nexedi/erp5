SELECT 
  gid
FROM syncml
WHERE
  path like <dtml-sqlvar path type="string">
<dtml-if strict_min_gid>
  AND gid > <dtml-sqlvar strict_min_gid type="string">
</dtml-if>
<dtml-if min_gid>
  AND gid >= <dtml-sqlvar min_gid type="string">
</dtml-if>
<dtml-if max_gid>
  AND gid <= <dtml-sqlvar max_gid type="string">
</dtml-if>
ORDER BY gid
<dtml-if limit>
  LIMIT <dtml-var limit>
</dtml-if>
