REQUEST = context.REQUEST

# First, find a cookie already made before.
COOKIE_NAME = 'configurator_user_preferred_language'
user_preferred_language = REQUEST.cookies.get(COOKIE_NAME, None)
if user_preferred_language is not None:
  # user already have explicitly selected language
  return user_preferred_language

# use language from browser's settings
configuration_language_list = []
for item in context.ConfiguratorTool_getConfigurationLanguageList():
  configuration_language_list.append(item[1])
http_accept_language = REQUEST.get('HTTP_ACCEPT_LANGUAGE', 'en')

for language_set in http_accept_language.split(','):
  language_tag = language_set.split(';')[0]
  language = language_tag.split('-')[0]
  if language in configuration_language_list:
    return language
return 'en'
