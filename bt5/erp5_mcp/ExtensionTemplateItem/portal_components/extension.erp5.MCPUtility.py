"""Utility functions for ERP5 MCP server"""

def PortalType_getViewActionText(portal_type):
  """Retrieve the raw TALES expression text for the 'view' action of a portal type."""
  for action_information in portal_type.getActionInformationList():
    if action_information.getReference() == "view":
      action_text = action_information.getAction().text
      return action_text
