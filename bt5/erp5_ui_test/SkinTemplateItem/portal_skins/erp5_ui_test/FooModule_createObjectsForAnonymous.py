"""Create objects with given parameters"""
from DateTime import DateTime

for i in range(start, start + num):
  foo = context.newContent(id=str(i), title="title_%s" % i, quantity=10.0 - float(i), portal_type=portal_type)
  foo.validate()

context.foo_module.manage_permission('Access contents information', ['Anonymous', 'Assignee', 'Assignor', 'Associate', 'Auditor', 'Author', 'Manager'], 0)
context.foo_module.manage_permission('View', ['Anonymous', 'Assignee', 'Assignor', 'Associate', 'Auditor', 'Author', 'Manager'], 0)

return 'Done'
