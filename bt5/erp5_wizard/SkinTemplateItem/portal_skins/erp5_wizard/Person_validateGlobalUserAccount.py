"""
 Validate persons on remote master server. 

 Only validate remote person/assigments if person 
 has reference and valid assigments. 
"""
from Products.ERP5Type.Log import log
if person is None:
  person = context

reference = person.getReference()
assignment_len = len(person.Person_getAvailableAssignmentValueList())
if reference is not None and assignment_len > 0:
  # validate user in Nexedi ERP5 only if its a loggable user in current instance
  kw = context.Person_getDataDict(person=person)
  context.portal_wizard.callRemoteProxyMethod(
                       'WitchTool_validateGlobalUserAccountFromExpressInstance', \
                       use_cache = 0, \
                       ignore_exceptions = 0, \
                       **kw)
else:
  log("Unable to validate remote global account for "\
      "%s (reference=%s , len(assignment_list)=%s)" % (person.getRelativeUrl(), 
                                                       reference, assignment_len))
