query_dict = {}
for key in kw.keys():
  if key == "portal_type":
    query_dict["portal_type"] = kw[key]
  else:
    query_dict[key] = dict(query=kw[key], key='ExactMatch')
result_list = context.portal_catalog(**query_dict)
owner_id = context.portal_membership.getAuthenticatedMember().getId()
functional_test_username = context.Base_getUserIdByUserName(context.Zuite_getHowToInfo()['functional_test_username'])
functional_another_test_username = context.Base_getUserIdByUserName(context.Zuite_getHowToInfo()['functional_another_test_username'])

for result in result_list:
  object = result.getObject()
  # check that every property of the research have been well taken in account
  for key in kw.keys():
    method_name = 'get%s' % (''.join([x.capitalize() for x in key.split('_')]))
    method = getattr(object, method_name)
    if strict_check_mode and method() != kw[key]:
      raise RuntimeError("One property is not the same that you wanted : you asked '%s' and expecting '%s' but get '%s'" % (key, kw[key], method()))
  # check that every object are owner by you
  if strict_check_mode and object.Base_getOwnerId() not in [owner_id, functional_test_username, 'System Processes','zope', functional_another_test_username]:
    raise RuntimeError("You have try to clean an item who haven't you as owner : %s is owned by %s and you are %s" %
         (object.getTitle(), object.Base_getOwnerId(), owner_id))

if strict_check_mode and max_count is not None:
  if len(result_list) <= max_count:
    if len(result_list) == 0:
      return None
    else:
      return result_list
  else:
    raise RuntimeError('The catalog return more item that you ask.')

if len(result_list) == 0:
  return None
return result_list
