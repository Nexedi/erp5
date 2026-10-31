portal = context.getPortalObject()

uid_mapping = {}

def REINDEXXXXXXXXXXXXXXXXXXXXXXX(obj):
  obj.recursiveReindexObject(activate_kw={'tag': 'module', 'priority': 2})

for _, obj in portal.portal_skins.ZopeFind(portal.portal_skins, obj_metatypes=('ERP5 Python Script', 'ERP5 Form', 'ERP5 Report'), search_sub=1):
  uid_mapping.setdefault(obj.getUid(), []).append(obj.getRelativeUrl())

for uid, relative_url_list in uid_mapping.items():
  print

  catalog_result_list = portal.portal_catalog(uid=uid, select_list=['relative_url',])

  # If 1 skin, and 1 result in catalog, with the same relative_url,
  # Then we are fine
  if len(catalog_result_list) == 1 and \
     len(relative_url_list) == 1 and \
     catalog_result_list[0].relative_url == relative_url_list[0]:
    print 'Nothing to do for ', relative_url_list[0]
    continue

  # Nothing is indexed for given uid
  elif len(catalog_result_list) == 0:
    print 'Nothing cataloged for %s' % relative_url_list
    # if there is more than 1 skin for the uid, we reindex one of them as such,
    # but we reset the uid for the others
    print 'Reindex %s with current uid' % relative_url_list[0]
    REINDEXXXXXXXXXXXXXXXXXXXXXXX(portal.restrictedTraverse(relative_url_list[0]))
    for relative_url in relative_url_list[1:]:
      print 'Set new uid and reindex %s' % relative_url
      obj = portal.restrictedTraverse(relative_url)
      obj.setUid(None)
      REINDEXXXXXXXXXXXXXXXXXXXXXXX(obj)
    continue

  # One skin indexed 2 times or more
  elif len(catalog_result_list) > 1:
    print 'To many result for uid ', uid, ' (%s)' % relative_url_list, '. PLEASE CHECK BY HAND'
    continue

  # For one uid, one object is found in catalog, but there are
  # more than one skin to install
  else:
    real_relative_url = catalog_result_list[0].relative_url
    print 'For uid ', uid, ', the skin ', real_relative_url, ' is already cataloged.'
    if len(relative_url_list) > 1:
      for relative_url in relative_url_list:
        if relative_url != real_relative_url:
          obj = portal.restrictedTraverse(relative_url)
          print 'Set new uid and reindex %s' % obj.getRelativeUrl()
          obj.setUid(None)
          REINDEXXXXXXXXXXXXXXXXXXXXXXX(obj)
  print '\n'

if dry:
  print 'DRY RUN'
  context.REQUEST.RESPONSE.write(printed)
  raise Exception('dry')
return printed
