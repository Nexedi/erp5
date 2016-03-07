context.getVcsTool().setLogin(auth, user, password)

return context.restrictedTraverse(caller)(**caller_kw)
