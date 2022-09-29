"""Get-or-Create Foo Line inside context (Foo object).

This script is used from Foo_viewFormBoxFooLine from a FormBox and thus
can receive 'field' and 'REQUEST' kwargs.
"""

foo_line_list = context.contentValues(portal_type='Foo Line')
if foo_line_list:
  return foo_line_list[0]

return context.newContent(portal_type='Foo Line')
