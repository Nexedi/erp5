from Products.ERP5Type.Message import translateString
obj = state_change['object']
request = container.REQUEST

error_list = []
warning_list = []
for message_dict in obj.checkSourceCode():
  message = '%s:%3d,%3d: %s' % (message_dict['type'],
                                  message_dict['row'],
                                  message_dict['column'],
                                  message_dict['text'])

  if message_dict['type'] in ('F', 'E'):
    error_list.append(message)
  else:
    warning_list.append(message)

if warning_list or error_list:
  request.set(
      'portal_status_message',
      translateString("Errors found in source code."))
  request.set('portal_status_level', 'error')

obj.setTextContentWarningMessageList(warning_list)
obj.setTextContentErrorMessageList(error_list)

if not error_list and obj.getValidationState() == 'modified':
  obj.checkConsistencyAndValidate()
