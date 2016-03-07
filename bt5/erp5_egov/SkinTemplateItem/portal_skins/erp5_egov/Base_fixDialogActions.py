"""This script fix dialog actions to add an empty dialog for object_print
actions that does not provide one.
"""
from Products.PythonScripts.standard import url_quote

if dialog_category != 'object_print':
  return actions.get(dialog_category, [])

def addDialogIfNeeded(url):
  '''If the action url is not a dialog, we add a generic print dialog.
  '''
  parts = url.split('/')
  absolute_url = '/'.join(parts[:-1])
  action = parts[-1]
  action_id = action.split('?')[0]
  form = getattr(context, action_id, None)
  #if not (hasattr(form, 'pt') and form.pt == 'form_dialog'):
  if form is not None:
    url = '%s/Base_viewIntermediatePrintDialog?dialog_action_url=%s' % (
                 context.absolute_url(), url_quote('%s/%s' % (absolute_url, action)))
  return url

print_action_list = actions['object_print']
new_print_action_list = []
for ai in print_action_list:
  ai_copy = ai.copy()
  # this is quite low level. It may require to be done from file system code in
  # the future.
  #ai_copy['original_url'] = ai_copy['url']
  #ai_copy['url'] = addDialogIfNeeded(ai_copy['url'])
  new_print_action_list.append( ai_copy )

return new_print_action_list
