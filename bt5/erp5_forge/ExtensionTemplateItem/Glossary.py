def getPropertySheetAttributeList(name):
  from Products.ERP5Type import PropertySheet
  class_ = PropertySheet.__dict__.get(name, None)
  result = []
  for i in getattr(class_, '_properties', ()):
    if 'acquired_property_id' in i:
      continue
    # we want to get only normal property.
    result.append(i['id'])
  return result


def getActionTitleListFromAllActionProvider(portal):
  result = {}
  provider_list = []
  for provider_id in portal.portal_actions.listActionProviders():
    if provider_id in ('portal_types', 'portal_workflow'):
      continue
    provider = getattr(portal, provider_id, None)
    if provider is None:
      continue
    provider_list.append(provider)

  for typeinfo in portal.portal_types.objectValues():
    provider_list.append(typeinfo)

  for action in provider.listActions():
      result[action.title] = None
  return result.keys()
