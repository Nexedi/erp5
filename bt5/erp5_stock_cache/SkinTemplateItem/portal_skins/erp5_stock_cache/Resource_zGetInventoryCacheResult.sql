SELECT 
  date, 
  result 
FROM 
  inventory_cache 
WHERE 
  inventory_cache.query=<dtml-sqlvar query type="string"> 
<dtml-if date>
  AND 
  inventory_cache.date <= <dtml-sqlvar date type="datetime">
</dtml-if>
ORDER BY 
  date DESC