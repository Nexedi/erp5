portal = context.getPortalObject()
if isinstance(site, str):
  site = portal.portal_categories.site.restrictedTraverse(site)
organisation = portal.organisation_module['site_%3s' % (site.getCodification(), )]
account_list = [x for x in organisation.objectValues(portal_type='Bank Account') if x.getValidationState() == 'valid']
if len(account_list) != 1:
  raise ValueError('Must not get %d account for the organisation %s' % (len(account_list), organisation.getTitleOrId()))
return account_list[0]
