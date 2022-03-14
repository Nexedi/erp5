certificate = context.getCertificate()
request = context.REQUEST
request.set('your_certificate', certificate['certificate'])
request.set('your_key', certificate['key'])
return context.Person_viewCertificateDialog()
