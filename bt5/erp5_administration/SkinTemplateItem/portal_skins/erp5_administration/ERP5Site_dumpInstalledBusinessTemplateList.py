for business_template in sorted(context.getPortalObject().portal_templates.contentValues(portal_type='Business Template'),
                  key=lambda x:x.getTitle()):
  if business_template.getInstallationState() == 'installed':
    print business_template.getTitle()

return printed
