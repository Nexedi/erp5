#https://lab.nexedi.com/nexedi/erp5/-/blob/master/product/ZSQLCatalog/SQLExpression.py#L42-44

import re


if not original_expression:
  return expression

def parse_select_aliases(select_expression):
  pattern = re.compile(
    r'([\w\(\)\*`\.]+(?:\s*\(\s*[\w\*`\.]*\s*\))?)\s+AS\s+(`\w+`|\w+)',
    re.IGNORECASE
  )
  return {
    alias.strip('`'): expr
    for expr, alias in pattern.findall(select_expression)
  }

SQL_LIST_SEPARATOR = ', '

expression_list = [x  for x in expression.split(SQL_LIST_SEPARATOR)]

new_expression_list = []

original_expression_dict = parse_select_aliases(original_expression)

for expression in expression_list:
  new_expression_list.append(original_expression_dict.get(expression, expression))

return SQL_LIST_SEPARATOR.join(new_expression_list)
