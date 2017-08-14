from zExceptions import Unauthorized
portal_preferences = context.getPortalObject().portal_preferences
if portal_preferences.isPreferredClusterDataNotebookEnabled():
  return True
raise Unauthorized('The asynchronous restricted implementation is not enabled on the server.')
