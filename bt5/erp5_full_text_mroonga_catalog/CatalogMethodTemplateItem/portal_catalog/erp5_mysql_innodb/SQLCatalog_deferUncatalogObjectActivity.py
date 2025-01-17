from Products.ERP5Type.Utils import ensure_list
uid_list = []
for grouped_message in grouped_message_list:
  assert not grouped_message.args
  assert ensure_list(grouped_message.kw.keys()) == ['uid']
  uid_list.append(grouped_message.kw['uid'])
for method_id in context.getSqlDeferredUncatalogObjectList():
  method = getattr(context, method_id)
  method(uid=uid_list)
for grouped_message in grouped_message_list:
  grouped_message.result = None
