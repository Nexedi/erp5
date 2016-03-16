configuration_save = context.restrictedTraverse(configuration_save_url)

organisation_configurator_item = configuration_save.addConfigurationItem(
    "Organisation Configurator Item",
    **kw)

context.setGlobalConfigurationAttr(company_email=kw.get('default_email_text'))

# store globally company's configurator item which we can use later to reconfigure
context.setGlobalConfigurationAttr(
     organisation_configurator_item=
          organisation_configurator_item.getRelativeUrl())
