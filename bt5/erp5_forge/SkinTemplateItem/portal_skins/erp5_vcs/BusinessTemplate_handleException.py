from erp5.component.module.Git import GitLoginError
from erp5.component.module.SubversionClient import SubversionSSLTrustError, SubversionLoginError
import json

kw = {}
method = 'view'
message = 'Unknown error'
try:
  raise exception
except SubversionSSLTrustError as e:
  message = 'SSL Certificate was not recognized'
  kw = dict(trust_dict=e.getTrustDict())
  method = 'BusinessTemplate_viewSvnSSLTrustDialog'
except SubversionLoginError as e:
  message = 'Server needs authentication, no cookie found'
  kw = dict(realm=e.getRealm(), username=context.getVcsTool().getPreferredUsername())
  method = 'BusinessTemplate_viewSvnLoginDialog'
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
