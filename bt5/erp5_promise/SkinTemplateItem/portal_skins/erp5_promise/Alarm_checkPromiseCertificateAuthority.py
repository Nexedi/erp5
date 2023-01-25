from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()

portal_certificate_authority = getattr(portal, 'portal_certificate_authority', None)
promise_ca_path = portal.getPromiseParameter('portal_certificate_authority', 'certificate_authority_path')
if promise_ca_path is None:
  severity = 0
  summary = "Nothing to do."
  detail = ""
else:
  if portal_certificate_authority is None:
    severity = 1
    summary = "Certificate Authority Tool is not present"
    detail = ""

  elif portal_certificate_authority.certificate_authority_path != promise_ca_path:
    severity = 1
    summary = "Certificate Authority Tool (OpenSSL)is not configured as Expected"
    detail = "Expect %s\nGot %s" % (portal_certificate_authority.certificate_authority_path, promise_ca_path)

  else:
    severity = 0
    summary = "Nothing to do."
    detail = ""

active_result = ActiveResult()
active_result.edit(
  summary=summary,
  severity=severity,
  detail=detail)

context.newActiveProcess().postResult(active_result)
