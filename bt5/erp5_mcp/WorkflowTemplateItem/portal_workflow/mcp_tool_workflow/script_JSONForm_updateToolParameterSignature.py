json_form = state_change['object']
portal = json_form.getPortalObject()
json_form_url = json_form.getRelativeUrl()
for tool in portal.portal_callables.objectValues(portal_type='MCP Tool'):
  specification = tool.getSpecificationValue()
  if specification is not None:
    if specification.getRelativeUrl() == json_form_url:
      tool.setParameterSignatureFromSpecification()
