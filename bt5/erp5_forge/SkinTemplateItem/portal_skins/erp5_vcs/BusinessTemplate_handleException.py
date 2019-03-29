from Products.ERP5VCS.Git import GitLoginError
from Products.ERP5VCS.SubversionClient import SubversionSSLTrustError, SubversionLoginError

try:
  raise exception
except SubversionSSLTrustError as e:
  message = 'SSL Certificate was not recognized'
  kw = dict(trust_dict=e.getTrustDict())
  method = 'BusinessTemplate_viewSvnSSLTrust'
except SubversionLoginError as e:
  message = 'Server needs authentication, no cookie found'
  kw = dict(realm=e.getRealm(), username=context.getVcsTool().getPreferredUsername())
  method = 'BusinessTemplate_viewSvnLogin'
except GitLoginError as e:
  message = str(e)
  kw = dict(remote_url=context.getVcsTool().getRemoteUrl())
  method = 'BusinessTemplate_viewGitLogin'

context.REQUEST.set('portal_status_message', message)
return getattr(context.asContext(**kw), method)(caller=caller, caller_kw=caller_kw)
