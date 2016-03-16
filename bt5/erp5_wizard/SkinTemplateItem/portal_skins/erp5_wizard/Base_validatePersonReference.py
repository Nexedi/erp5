"""
  THis script is called from UI for creating a global account. In case of remote server failure
  return 0 which will stop user and show an explanation message.
"""
try:
  return int(context.WizardTool_isPersonReferenceGloballyUnique(editor, request, ignore_users_from_same_instance))
except:
  return 0
