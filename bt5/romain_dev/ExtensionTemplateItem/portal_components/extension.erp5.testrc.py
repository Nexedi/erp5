def testrc(self):
  result = ''
  portal = self.getPortalObject()

  selection = portal.portal_selections.getSelectionFor('person_module_selection')
  key_list = selection.__dict__.keys()
  key_list.sort()
  for key in key_list:
    result += '%s: %s\n' % (key, selection.__dict__[key])
  return result
  return str(selection.__dict__)

  print selection.checked_uids
  print selection.domain_path
  print selection.domain_list
  if selection.domain is not None:
    print selection.domain.asDomainDict()

  return printed
  return 'couscous'