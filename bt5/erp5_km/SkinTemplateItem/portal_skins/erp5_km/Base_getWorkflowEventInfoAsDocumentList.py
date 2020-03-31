from Products.ERP5Type.Document import newTempBase

request = context.REQUEST

# we can use current_web_document in case it's "embedded" into a Web Section
document = request.get('current_web_document', context)

event_document_list = []
event_list = document.Base_getWorkflowEventInfoList()
for event in event_list:
  event_document = newTempBase(context, 'Event Info')
  event_document.edit(**{'date': event.time,
                         'action': event.action,
                         'actor': event.actor
                        })
  event_document_list.append(event_document)

return event_document_list
