"""Check that the bank account "belong" to the destination section.
"""
portal = context.getPortalObject()
if source:
  section = context.getSourceSectionValue(portal_type=portal.getPortalEntityTypeList())
  bank_account = context.getSourcePaymentValue(portal_type=portal.getPortalPaymentNodeTypeList())
else:
  section = context.getDestinationSectionValue(portal_type=portal.getPortalEntityTypeList())
  bank_account = context.getDestinationPaymentValue(portal_type=portal.getPortalPaymentNodeTypeList())

if section is None or bank_account is None:
  return True
section = section.Organisation_getMappingRelatedOrganisation()
return bank_account.getParentValue() == section
