"""Returns the default text format for response events.

This script is here so that we can easily customized depending on the context event, ticket or user preferences.
"""
return context.getContentType()\
  or context.getPortalObject().portal_preferences.getPreferredTextFormat()
