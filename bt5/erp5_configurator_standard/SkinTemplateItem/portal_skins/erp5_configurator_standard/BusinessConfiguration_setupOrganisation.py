configuration_save = context.restrictedTraverse(configuration_save_url)
company_email = kw['default_email_text']

# create under 'portal_categories/group' a new category using company title
group_id = 'my_group' #'_'.join(kw['title'].split(' '))[:20]

organisation_configurator_item = configuration_save.addConfigurationItem(
    "Organisation Configurator Item",
    group=group_id,
    site='main',
    **kw)

configuration_save.addConfigurationItem("Category Configurator Item",
                                        category_root='group',
                                        object_id=group_id,
                                        title=kw['title'])

# store globally group_id
context.setGlobalConfigurationAttr(group_id=group_id)

# store globally company's email
context.setGlobalConfigurationAttr(company_email=company_email)

# store globally company's configurator item which we can use later to reconfigure
context.setGlobalConfigurationAttr(
     organisation_configurator_item=
          organisation_configurator_item.getRelativeUrl())
