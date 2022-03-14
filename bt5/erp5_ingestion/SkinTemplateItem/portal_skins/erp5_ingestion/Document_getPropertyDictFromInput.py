return_dict = {}

# All properties that portal_contributions.newContent expose
# in its signature that shouldn't be stored on document itself
technical_argument_list = ('url', 'container', 'container_path', 'discover_metadata', 'user_login',)
for key, value in list(argument_dict.items()):
  if key not in technical_argument_list and value not in (None, ''):
    return_dict[key] = value

return return_dict
