"""return first foo line or context
"""
foo_line_list = context.contentValues(portal_type='Foo Line')
if foo_line_list:
  return foo_line_list[0]
return context
