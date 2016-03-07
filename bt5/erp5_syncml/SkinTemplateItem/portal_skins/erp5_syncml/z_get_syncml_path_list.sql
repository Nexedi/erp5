SELECT path, gid, data 
FROM syncml
WHERE
  path like <dtml-sqlvar path type="string">
<dtml-if min_gid>
  AND gid >= <dtml-sqlvar min_gid type="string">
</dtml-if>
<dtml-if max_gid>
  AND gid <= <dtml-sqlvar max_gid type="string">
</dtml-if>
