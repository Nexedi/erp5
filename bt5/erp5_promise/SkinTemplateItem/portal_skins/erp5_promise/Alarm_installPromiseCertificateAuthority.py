portal = context.getPortalObject()

portal_certificate_authority = getattr(portal, 'portal_certificate_authority', None)
promise_ca_path = portal.getPromiseParameter('portal_certificate_authority', 'certificate_authority_path')

if portal_certificate_authority is None:
   portal.manage_addProduct['ERP5'].manage_addTool('ERP5 Certificate Authority Tool', None)
   portal_certificate_authority = getattr(portal, 'portal_certificate_authority')

portal_certificate_authority.manage_editCertificateAuthorityTool(
   certificate_authority_path=promise_ca_path)
