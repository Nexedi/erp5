contains_more_than_uid = set(['uid']).isdisjoint

uid_list = []
for grouped_message in grouped_message_list:
  assert not grouped_message.args
  assert not contains_more_than_uid(grouped_message.kw)
  uid_list.append(grouped_message.kw['uid'])
for method_id in context.getSqlDeferredUncatalogObjectList():
  method = getattr(context, method_id)
  method(uid=uid_list)
for grouped_message in grouped_message_list:
  grouped_message.result = None
