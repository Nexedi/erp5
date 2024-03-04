item_list = None
if message.activity[3:].lower() == "dict":
  item_list = context.ActivityTool_zGetDateForSQLDictMessage(uid=str(message.uid))

elif message.activity[3:].lower() == "queue":
  item_list = context.ActivityTool_zGetDateForSQLQueueMessage(uid=str(message.uid))

if item_list is not None and len(item_list) == 1:
  return item_list[0].date

raise ValueError("Unknown Message Type, so we cannot select proper table %s " % message.activity[3:])
