obj = state_change['object']

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

obj.setTextContentWarningMessageList(warning_list)
obj.setTextContentErrorMessageList(error_list)

if not error_list and obj.getValidationState() == 'modified':
  obj.checkConsistencyAndValidate()
