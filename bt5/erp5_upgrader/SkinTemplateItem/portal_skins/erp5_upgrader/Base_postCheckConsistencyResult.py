active_process = context.getPortalObject().restrictedTraverse(active_process)

with context.defaultActivateParameterDict(activate_kw, placeless=True):
  constraint_message_list = context.checkConsistency(
    fixit=fixit, filter=filter_dict,)

if constraint_message_list and not active_process.getResultList():
  active_process.postActiveResult(
    severity=0 if fixit else 1,
    summary="%s Consistency - At least one inconsistent object found" % ('Fix' if fixit else 'Check', ),
    detail=[m.message for m in constraint_message_list])
