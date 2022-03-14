from builtins import range
configuration_save_url = kw.get('configuration_save_url', None)
configuration_save = context.restrictedTraverse(configuration_save_url)

user_number = context.getGlobalConfigurationAttr('user_number')

## get only form keys
form_keys = [i for i in list(kw.keys()) if i.startswith('field_your_') and i!='field_your_search_text']


function = "function/runmydocs_user/assignor"
if user_number == 1:
  # only one user
  for key in ('configuration_save_url', 'transition', 'client_id', 'password_confirm'):
    kw.pop(key, None)
  configuration_save.addConfigurationItem("Person Configurator Item",
                                          function=function,
                                          **kw)
else:
  # many users
  for counter in range(user_number):
    user_kw = {}
    for key in form_keys:
      new_key = key.replace("field_your_", "")
      value = kw.get(key)
      if value:
        user_kw[new_key] = value[counter]
    # add an user
    user_kw.pop('password_confirm', None)
    configuration_save.addConfigurationItem("Person Configurator Item",
                                            function=function,
                                            **user_kw)
