# Return by default previous user input

sql_expression = context.REQUEST.get('sql_expression', None)
if sql_expression: return sql_expression

# Else return this string, which could be made more dynamic in the future
# to take into account the context


return """
SELECT
  catalog.uid,
  catalog.path,
  <ADD YOUR COLUMNS>
FROM
  catalog,
  <DEFINE ANOTHER TABLE>,
  <DEFINE YET ANOTHER TABLE>
WHERE
  catalog.uid = <OTHER TABLE>.uid
AND
  <DEFINE MORE EXPRESSION>
ORDER BY
  catalog.id ASC
GROUP BY
  <DEFINE GROUPS>
"""
