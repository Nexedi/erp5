# searching
# processing_node column is manage by methods called by getMessageTempObjectList
if kw.get('processing_node', None) == '':
  del kw['processing_node']

message_kw = dict([(k,kw[k]) for k in ['uid_activity','str_object_path','method_id',
                                       'args','retry','processing_node',
                                       'processing'] if not(kw.get(k) in ('',None))])
if message_kw.has_key("str_object_path"):
  message_kw["path"] = message_kw.pop("str_object_path")
if message_kw.has_key("uid_activity"):
  message_kw["uid"] = message_kw.pop("uid_activity")

message_list = context.getMessageTempObjectList(**message_kw)
message_list_to_show = []
while len(message_list) > 0:
  message = message_list.pop(0)
  message.edit(str_object_path = '/'.join(str(i) for i in message.object_path))
  message.edit(uid_activity = str(message.uid) + ' ('+ message.activity[3:] +')')
  message.edit(arguments = str(message.args))
  message.edit(delete = '[Delete]')
  message.edit(restart = '[Restart]')
  message_list_to_show.append(message)

return message_list_to_show
