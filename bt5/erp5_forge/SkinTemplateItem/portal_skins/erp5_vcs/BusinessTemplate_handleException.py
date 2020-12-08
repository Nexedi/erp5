from erp5.component.module.Git import GitLoginError
from erp5.component.module.SubversionClient import SubversionSSLTrustError, SubversionLoginError
import json

try:
  raise exception
except SubversionSSLTrustError, e:
  message = 'SSL Certificate was not recognized'
  kw = dict(trust_dict=e.getTrustDict())
  method = 'BusinessTemplate_viewSvnSSLTrust'
except SubversionLoginError, e:
  message = 'Server needs authentication, no cookie found'
  kw = dict(realm=e.getRealm(), username=context.getVcsTool().getPreferredUsername())
  method = 'BusinessTemplate_viewSvnLogin'
except GitLoginError, e:
  message = str(e)
  kw = dict(remote_url=context.getVcsTool().getRemoteUrl())
  method = 'BusinessTemplate_viewGitLogin'

commit_dict['caller'] = caller
# XXX caller_kw
# Always propage all informations throught formulator hidden field
request = context.REQUEST
request.form['your_commit_json'] = json.dumps(commit_dict)

return context.Base_renderForm(method, keep_items={
  'portal_status_message': message
})
