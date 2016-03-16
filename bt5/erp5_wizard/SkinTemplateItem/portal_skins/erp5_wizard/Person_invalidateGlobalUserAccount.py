"""
 Invalidate global user account. 

 Only invalidate if the local user has no Valid Assigments and 
 reference.
"""
if person is None:
  person = context

reference = person.getReference()
assignment_len = len(person.Person_getAvailableAssignmentValueList())
if reference is not None and  assignment_len == 0:
  # invalidate user in Authentification Server only if 
  # its a loggable user in current instance
  kw = context.Person_getDataDict(person=person)
  context.portal_wizard.callRemoteProxyMethod(
                     'WitchTool_invalidateGlobalUserAccountFromExpressInstance', \
                     use_cache = 0, \
                     ignore_exceptions = 0, \
                     **kw)
else:
  from Products.ERP5Type.Log import log
  log("Unable to invalidate remote global account for "\
      "%s (reference=%s , len(assignment_list)=%s)" % (person.getRelativeUrl(), 
                                                       reference, assignment_len))
