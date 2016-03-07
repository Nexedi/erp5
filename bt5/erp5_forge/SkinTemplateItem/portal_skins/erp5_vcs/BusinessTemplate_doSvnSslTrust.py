request = context.REQUEST
trust_dict=dict((x, request[x]) for x in (
  'valid_until', 'hostname', 'realm', 'finger_print', 'valid_from', 'issuer_dname', 'failures'))

context.getVcsTool().acceptSSLServer(trust_dict, True)

return context.restrictedTraverse(caller)(**caller_kw)
