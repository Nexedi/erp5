"""
  This scripts sets up automatically default parameters
  for a newly created Web Site
"""
# Set Web Site layout to default one
context.setContainerLayout('erp5_web_layout')
context.setContentLayout('erp5_web_content_layout')
context.setLayoutConfigurationFormId('WebSection_viewDefaultThemeConfiguration')
# At least one available language is required
context.setAvailableLanguageSet([context.Localizer.get_selected_language()])
context.setStaticLanguageSelection(1)
