from zExceptions import Forbidden

preference_tool = context.getPortalObject().portal_preferences
if preference_tool.isPreferredHtmlStyleDisabled():
  raise Forbidden('xhtml_style is disabled. Please use ERP5JS')

pass
