# Return by default previous user input

python_expression = context.REQUEST.get('python_expression', None)
if python_expression:
  return python_expression

# Else return this string, which could be made more dynamic in the future
# to take into account the context


return """kw={'portal_type': 'Person'}
return context.portal_catalog(**kw)"""
