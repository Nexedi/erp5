from Products.ERP5Type.Utils import ensure_list
for k, v in ensure_list(kw.items()):
  if v:
    if k == "str_object_path":
      kw["path"] = v
    elif k == "uid_activity":
      kw["uid"] = v
    elif k in ('method_id', 'processing_node', 'retry', 'date'):
      continue
  del kw[k]

message_list = context.getMessageTempObjectList(**kw)
for message in message_list:
  message.edit(
    str_object_path = '/'.join(message.object_path),
    uid_activity = str(message.uid) + ' ('+ message.activity[3:] +')',
    delete = '[Delete]',
    restart = '[Restart]',
  )

return message_list
