from erp5.component.module.Git import GitLoginError
from erp5.component.module.SubversionClient import SubversionSSLTrustError, SubversionLoginError

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

context.REQUEST.set('portal_status_message', message)
return getattr(context.asContext(**kw), method)(caller=caller, caller_kw=caller_kw)
