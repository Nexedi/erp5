SELECT
  CASE 
    WHEN (mirror_date=date) THEN 
      SUM(quantity)
    ELSE
      SUM(quantity * TIME_TO_SEC(TIMEDIFF(LEAST(<dtml-sqlvar expr="to_date" type="datetime">, mirror_date), 
                                          GREATEST(date, <dtml-sqlvar expr="from_date" type="datetime">))) / 
                     TIME_TO_SEC(TIMEDIFF(mirror_date, date)))
  END AS total_quantity,
  <dtml-sqlvar expr="from_date" type="datetime"> AS from_date,
  <dtml-sqlvar expr="to_date" type="datetime"> AS to_date
FROM
  stock
WHERE
  (date < <dtml-sqlvar expr="to_date" type="datetime">) 
AND 
  (mirror_date >= <dtml-sqlvar expr="from_date" type="datetime">)
AND
  node_uid in (
    <dtml-in node>
      <dtml-sqlvar sequence-item type="int">
      <dtml-unless sequence-end>, </dtml-unless> 
    </dtml-in node> )

<dtml-if resource>
  AND
  resource_uid in (
    <dtml-in resource>
      <dtml-sqlvar sequence-item type="int">
      <dtml-unless sequence-end>, </dtml-unless> 
    </dtml-in resource> )
</dtml-if>

AND
  portal_type in (
    <dtml-in portal_type>
      <dtml-sqlvar sequence-item type="string">
      <dtml-unless sequence-end>, </dtml-unless> 
    </dtml-in portal_type> )