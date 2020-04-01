import re
message_re = re.compile(r'[CRWEF]:\s*(?P<line>\d+),\s*(?P<column>\d+):\s*.*')

def getParsedMessageList(message_list):
  result_list = []
  for message in message_list:
    line = None
    column = None
    message_obj = message_re.match(message)
    if message_obj:
      line = int(message_obj.group('line'))
      column = int(message_obj.group('column'))

    result_list.append({'line': line, 'column': column, 'message': message})

  return result_list

import json
return json.dumps({'error_list': getParsedMessageList(context.getTextContentErrorMessageList()),
                   'warning_list': getParsedMessageList(context.getTextContentWarningMessageList())})
