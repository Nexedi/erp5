context.ERP5Site_assertClusterDataNotebookEnabled()
if context.hasErrorActivity():
  return 'Error'
elif context.hasActivity():
  return 'Running'
else:
  return 'Ready'
