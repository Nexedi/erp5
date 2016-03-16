DELETE 
FROM 
  inventory_cache 
WHERE 
  date > (SELECT min(date) from stock where <dtml-sqltest uid_list column=uid type=int multiple>)
<dtml-if min_date>
OR
  date > <dtml-sqlvar expr="min_date" type="datetime">
</dtml-if>

