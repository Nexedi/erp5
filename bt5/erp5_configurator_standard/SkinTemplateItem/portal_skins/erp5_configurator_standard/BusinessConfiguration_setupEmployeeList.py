configuration_save_url = kw.get('configuration_save_url', None)
configuration_save = context.restrictedTraverse(configuration_save_url)
organisation_id = context.getGlobalConfigurationAttr('organisation_id')
group_id = context.getGlobalConfigurationAttr('group_id')

company_employees_number = context.getGlobalConfigurationAttr('company_employees_number')

## get only form keys
form_keys = [i for i in kw.keys() if i.startswith('field_your_') \
                         and i not in ['field_your_search_text', 'field_your_business_configuration']]

if company_employees_number==1:
  # only one employee
  for key in ('configuration_save_url', 'transition', 'client_id', 'password_confirm'):
    kw.pop(key, None)
  function = kw.pop('function', None)
  configuration_save.addConfigurationItem("Person Configurator Item",
                                           organisation_id = organisation_id,
                                           function = function,
                                           group_id = group_id,
                                            **kw)
else:
  # many employees
  for employee_counter in range(0, company_employees_number):
    employee_kw = {}
    for key in form_keys:
      new_key = key.replace("field_your_", "")
      employee_kw[new_key] = kw[key][employee_counter]
    # add an emlpoyee
    function = employee_kw.pop('function', None)
    employee_kw.pop('password_confirm', None)
    configuration_save.addConfigurationItem("Person Configurator Item",
                                            organisation_id = organisation_id,
                                            function = function,
                                            group_id = group_id,
                                            **employee_kw)
