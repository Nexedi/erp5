SELECT
	SUM(movement.quantity) AS quantity
FROM
	catalog AS container_cell, movement
WHERE
	movement.explanation_uid = <dtml-sqlvar explanation_uid type="int">
  AND container_cell.has_cell_content = 0
  AND container_cell.uid = movement.uid
  AND	(container_cell.portal_type = "Container Cell" 
      OR container_cell.portal_type = "Container Line")

<dtml-if resource_uid>
  AND movement.resource_uid = <dtml-sqlvar resource_uid type="int">
</dtml-if>
<dtml-if variation_text>
  AND movement.variation_text = <dtml-sqlvar variation_text type="string">
</dtml-if>
