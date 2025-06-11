editor = context.getPortalObject().portal_preferences.getPreferredSourceCodeEditor('text_area')
editor_configuration_list = [('editor', editor), ('portal_type', context.getPortalType()), ('maximize', 'listbox' not in field.id), ('content_type', context.getProperty('content_type'))]
if editor == 'monaco':
  editor_configuration_list.append(('python_script_header', context.PythonScript_getFunctionDefinitionForCodeAnalysis()))

return editor_configuration_list
