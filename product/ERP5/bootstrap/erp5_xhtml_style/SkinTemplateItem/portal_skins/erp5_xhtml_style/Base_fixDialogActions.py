"""This script fix dialog actions to add an empty dialog for object_print
actions that does not provide one.
"""
from Products.PythonScripts.standard import url_quote

if dialog_category == 'object_report':
  return sorted(actions.get('object_report', []) + actions.get('object_jio_report', []), key=lambda x: x["priority"])
elif dialog_category == 'object_exchange':
  return sorted(actions.get('object_exchange', []) + actions.get('object_jio_exchange', []), key=lambda x: x["priority"])
elif dialog_category == 'object_action':
  return sorted(actions.get('object_action', []) + actions.get('object_jio_action', []), key=lambda x: x["priority"])
elif dialog_category == 'object_fast_input':
  return sorted(actions.get('object_fast_input', []) + actions.get('object_jio_fast_input', []), key=lambda x: x["priority"])
if dialog_category != 'object_print':
  return actions.get(dialog_category, [])


def addDialogIfNeeded(url):
  '''If the action url is not a dialog, we add a generic print dialog.
  '''
  parts = url.split('/')
  absolute_url = '/'.join(parts[:-1])
  action = parts[-1]
  action_list = action.split('?')
  action_id = action_list[0]
  form = getattr(context, action_id, None)

  # try to get format parameter if exists
  parameter_kw = {}
  format = ''
  if len(action_list) > 1:
    parameter_list = action.split('?')[1]
    parameter_tuple_list = [tuple(tuple_parameter.split('=')) for tuple_parameter in parameter_list.split('&')]
    parameter_kw = dict(parameter_tuple_list)
  meta_type = getattr(form, 'meta_type', None)
  if meta_type in ('ERP5 Form Printout', 'ERP5 OOo Template',):
    # The target is a Form Printout or OOoTemplate so use dedicated form_dialog to enable
    # conversion and/or deferred reporting
    if meta_type == 'ERP5 Form Printout':
      base_content_type = getattr(form, form.template).getProperty('content_type')
    else:
      base_content_type = form.getProperty('content_type')
    if parameter_kw.has_key('format'):
      # if format is passed in action url: remove it
      format = parameter_kw.pop('format')
      action = '%s?%s' % (action_id, '&'.join(['='.join(tuple_parameter) for tuple_parameter in parameter_kw.items()]))
    url = '%s/Base_viewOOoPrintDialog?dialog_action_url=%s&base_content_type=%s&field_your_format=%s' % (
                 context.absolute_url(),
                 url_quote('%s/%s' % (absolute_url, action)),
                 url_quote(base_content_type),
                 url_quote(format))
  elif not (hasattr(form, 'pt') and form.pt == 'form_dialog'):
    url = '%s/Base_viewIntermediatePrintDialog?dialog_action_url=%s' % (
                 context.absolute_url(), url_quote('%s/%s' % (absolute_url, action)))
  return url

print_action_list = sorted(actions.get('object_print', []) + actions.get('object_jio_print', []), key=lambda x: x["priority"])
new_print_action_list = []
for ai in print_action_list:
  ai_copy = ai.copy()
  # this is quite low level. It may require to be done from file system code in
  # the future.
  ai_copy.update(dict(
                    original_url=ai_copy['url'],
                    url=addDialogIfNeeded(ai_copy['url'])))
  new_print_action_list.append( ai_copy )

return new_print_action_list
