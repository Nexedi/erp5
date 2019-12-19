"""Create document of `portal_type` inside `parent` or Accounting Module.

`embedded` is a list of documents to create inside the top-level document
`simulation_state` is known to be a workflow transition variable thus we correctly
                   use workflows to change the state
"""
portal = context.getPortalObject()
parent = parent or portal.accounting_module
document = parent.newContent(portal_type=portal_type, **kwargs)

for embed in embedded:
  script(parent=document, **embed)

if simulation_state == 'planned':
  document.plan()
elif simulation_state == 'validated':
  document.validate()
elif simulation_state == 'confirmed':
  document.confirm()
elif simulation_state in ('stopped', 'delivered'):
  document.stop()
  if simulation_state == 'delivered':
    document.deliver()

return document
