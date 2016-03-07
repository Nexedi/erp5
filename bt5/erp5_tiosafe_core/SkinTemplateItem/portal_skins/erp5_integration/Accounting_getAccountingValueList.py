"""
  Find the list of objects to synchronize by calling the catalog.

  Possibly look up a single object based on its ID, GID
"""
accounting_list = []
if not id:
  for accounting in context.accounting_module.objectValues():
    if accounting.getReference() and accounting.getStartDate() and accounting.getSimulationState() != 'deleted':
      accounting_list.append(accounting)
  return accounting_list
accounting = getattr(context.accounting_module, id)
if accounting.getReference() and accounting.getStartDate() and accounting.getSimulationState() != 'deleted':
  accounting_list.append(accounting)
return accounting_list
