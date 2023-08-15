parent = context.getParentValue()

if parent.getPortalType() == "Person":
  parent.checkCertificateRequest()

certificate = context.getCertificate()
request = context.REQUEST
request.set('your_certificate', certificate['certificate'])
request.set('your_key', certificate['key'])
return context.CertificateLogin_viewCertificateDialog(
  keep_items = {'portal_status_message' : 'Certificate generated.'}
)
