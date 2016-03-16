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
