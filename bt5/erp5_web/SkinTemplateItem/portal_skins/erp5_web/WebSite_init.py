"""
  This scripts sets up automatically default parameters
  for a newly created Web Site
"""
# Set Web Site layout to default one
context.setContainerLayout('erp5_web_layout')
context.setContentLayout('erp5_web_content_layout')
context.setLayoutConfigurationFormId('WebSection_viewDefaultThemeConfiguration')
language_list = context.Localizer.get_supported_languages()
context.setAvailableLanguageSet(language_list)
context.setStaticLanguageSelection(1)
