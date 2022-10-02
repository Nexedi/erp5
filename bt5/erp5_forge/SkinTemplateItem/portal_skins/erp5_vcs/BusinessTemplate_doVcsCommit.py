import json
from six import string_types as basestring

commit_dict = json.loads(commit_json) if commit_json is not None else {
  'added': (),
  'modified': (),
  'removed': (),
  'changelog': '',
  'push': False
}

for key, file_list in (('added', added), ('modified', modified), ('removed', removed)):

  if file_list is not None:
    # XXX: ERP5VCS_doCreateJavaScriptStatus should send lists
    if isinstance(file_list, basestring):
      file_list = file_list != 'none' and filter(None, file_list.split(',')) or ()
    commit_dict[key] = file_list

if changelog is not None:
  commit_dict['changelog'] = changelog
if push is not None:
  commit_dict['push'] = push

# Remover keys used when handling commit exception
commit_dict.pop('caller', None)
commit_dict.pop('caller_kw', None)

# Always propage all information throught formulator hidden field
request = context.REQUEST
request.form['your_commit_json'] = json.dumps(commit_dict)
request.form['your_added'] = commit_dict['added']
request.form['your_modified'] = commit_dict['modified']
request.form['your_removed'] = commit_dict['removed']

if commit_dict['changelog'].strip():
  request.form['your_changelog'] = commit_dict['changelog']
else:
  from Products.ERP5Type.Message import translateString
  error_msg = "Please set a ChangeLog message."
  return context.Base_renderForm('BusinessTemplate_viewVcsChangelogDialog', keep_items={
    'portal_status_message': translateString(error_msg),
    'cancel_url': context.absolute_url() +
      '/BusinessTemplate_viewVcsStatus?do_extract:int=0'
      '&portal_status_message=Commit%20cancelled.'
  })

try:
  return context.getVcsTool().commit(
    commit_dict['changelog'],
    commit_dict['push'],
    added=commit_dict['added'],
    modified=commit_dict['modified'],
    removed=commit_dict['removed']
  )
except Exception as error:
  return context.BusinessTemplate_handleException(error, script.id, commit_dict)
