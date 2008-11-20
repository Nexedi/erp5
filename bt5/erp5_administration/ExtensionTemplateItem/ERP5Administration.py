def dumpWorkflowChain(self):
  # This method outputs the workflow chain in the format that you can
  # easily get diff like the following:
  # ---
  # Account,account_workflow
  # Account,edit_workflow
  # ...
  # ---
  workflow_tool = self.getPortalObject().portal_workflow
  cbt = workflow_tool._chains_by_type
  ti = workflow_tool._listTypeInfo()
  types_info = []
  for t in ti:
    id = t.getId()
    title = t.Title()
    if title == id:
      title = None
    if cbt is not None and cbt.has_key(id):
      chain = sorted(cbt[id])
    else:
      chain = ['(Default)']
    types_info.append({'id': id,
                       'title': title,
                       'chain': chain})
  output = []
  for i in sorted(types_info, key=lambda x:x['id']):
    for chain in i['chain']:
      output.append('%s,%s' % (i['id'], chain))
  return '\n'.join(output)
