portal = context.getPortalObject()

portal_certificate_authority = portal.portal_certificate_authority
promise_ca_path = portal.getPromiseParameter('portal_certificate_authority', 'certificate_authority_path')
portal_certificate_authority.manage_editCertificateAuthorityTool(
   certificate_authority_path=promise_ca_path)
