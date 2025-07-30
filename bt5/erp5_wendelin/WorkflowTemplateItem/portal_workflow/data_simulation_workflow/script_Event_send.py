event = state_change['object']

send_method = event.getTypeBasedMethod('send')
parameter_list = ('from_url', 'to_url', 'reply_url', 'subject',
                  'body', 'attachment_format', 'attachment_list',)
if getattr(send_method, 'meta_type', None) == 'Script (Python)':
  parameter_list = send_method.ZScriptHTML_tryParams()

# Turn the SafeMapping from keyword arguments into a dict.
kwargs = {}
for key in parameter_list:
  state_change_arg = state_change['kwargs'].get(key)
  if state_change_arg:
    kwargs[key] = state_change_arg
  
event.send(**kwargs) # will call type based method
