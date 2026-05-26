from erp5.component.module.Git import GitLoginError
import json

kw = {}
method = 'view'
message = 'Unknown error'
try:
  raise exception
except GitLoginError as e:
  message = str(e)
  kw = dict(remote_url=context.getVcsTool().getRemoteUrl())
  method = 'BusinessTemplate_viewGitLoginDialog'

commit_dict['caller'] = caller
# Always propage all information throught formulator hidden field
request = context.REQUEST
request.form['your_commit_json'] = json.dumps(commit_dict)

return context.asContext(**kw).Base_renderForm(method, keep_items={
  'portal_status_message': message
})
