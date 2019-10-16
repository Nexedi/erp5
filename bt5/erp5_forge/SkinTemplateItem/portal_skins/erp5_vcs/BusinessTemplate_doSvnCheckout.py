from erp5.component.module.SubversionClient import SubversionSSLTrustError, SubversionLoginError

vcs_tool = context.getVcsTool()
try:
  entry_dict = vcs_tool.checkout(context, url)
except SubversionSSLTrustError, error:
  context.REQUEST.set('portal_status_message', 'SSL Certificate was not recognized')
  return context.asContext(trust_dict = error.getTrustDict(), caller='info').BusinessTemplate_viewSvnSSLTrust()
except SubversionLoginError, error1 :
  context.REQUEST.set('portal_status_message', 'Server needs authentication, no cookie found')
  return context.asContext(caller='info', realm = error1.getRealm(), username = vcs_tool.getPreferredUsername()).BusinessTemplate_viewSvnLogin()
return entry_dict
return context.asContext(entry_dict=entry_dict).BusinessTemplate_viewSvnInfos()
