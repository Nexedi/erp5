if caller_kw is None:
  caller_kw = {}
context.getVcsTool().setLogin(auth, user, password)

return context.restrictedTraverse(caller)(**caller_kw)
