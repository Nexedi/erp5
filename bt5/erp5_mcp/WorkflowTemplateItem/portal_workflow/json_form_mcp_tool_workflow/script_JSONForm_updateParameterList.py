json_form = state_change['object']
for tool in json_form.Base_getRelatedObjectList(portal_type="MCP Tool"):
  tool.setParameterSignatureFromSpecification()
