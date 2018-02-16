portal = context.getPortalObject()
portal_diff = portal.portal_diff

first_document = portal.restrictedTraverse(first_document_path)
second_document = portal.restrictedTraverse(second_document_path)

diff = portal_diff.diffPortalObject(fisrt_document, second_document).asBeautifiedJSONDiff()
applicable_diff_list = []

for i in checked_uid_list:
  try:
    applicable_diff_list.append(diff[i])
  except IndexError:
    pass

return applicable_diff_list
