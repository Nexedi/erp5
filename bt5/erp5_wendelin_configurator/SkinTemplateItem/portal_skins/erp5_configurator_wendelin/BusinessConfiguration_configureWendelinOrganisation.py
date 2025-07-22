configuration_save = context.restrictedTraverse(configuration_save_url)
company_email = kw['default_email_text']
group = kw['group']

organisation_configurator_item = configuration_save.addConfigurationItem(
                                     "Organisation Configurator Item", **kw)

# store globally preferred group
context.setGlobalConfigurationAttr(group_id=group)

# store globally company's email
context.setGlobalConfigurationAttr(company_email=company_email)

# store globally company's configurator item which we can use later to reconfigure
context.setGlobalConfigurationAttr(organisation_configurator_item=organisation_configurator_item.getRelativeUrl())

# price currency contains all currency info like iso code& precision ';' separated
currency_info_list = kw['price_currency_list']
for currency_info in currency_info_list:
  currency_reference, currency_base_unit_quantity, currency_title  = \
      currency_info.split(';')
  configuration_save.addConfigurationItem(
      "Currency Configurator Item",
      reference = currency_reference,
      base_unit_quantity = currency_base_unit_quantity,
      title = currency_title,)
context.setGlobalConfigurationAttr(default_currency=currency_reference)
