parent = context.getParentValue()

if parent.getPortalType() == "Person":
  parent.checkCertificateRequest()

context.revokeCertificate()
return context.Base_redirect(form_id, keep_items = {'portal_status_message' : 'Certificate revoked.'},  **kw)
