if ignore_business_template_list is None:
  ignore_business_template_list = []
for business_template in sorted(context.getPortalObject().portal_templates.contentValues(portal_type='Business Template'),
                  key=lambda x:x.getTitle()):
  if business_template.getInstallationState() == 'installed' and \
    business_template.getTitle() not in ignore_business_template_list:
    print(business_template.getTitle())

return printed
