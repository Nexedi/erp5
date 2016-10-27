SELECT
  reference, portal_type
FROM
  catalog
WHERE
  portal_type in (<dtml-in expr="portal_catalog.getPortalLoginTypeList()"><dtml-sqlvar sequence-item type="string"><dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
  AND validation_state='validated'
GROUP BY
  reference, portal_type
HAVING
  count(*) > 1
