from Products.DCWorkflow.DCWorkflow import ValidationFailed
# Make a constraint, it is easier
request_eform = state_change['object']
portal = request_eform.getPortalObject()
organisation_module = portal.organisation_module
person_module = portal.person_module
date = request_eform.getDate()
if request_eform.getPortalType() == 'P2':
  organisation_list = portal.portal_catalog(parent_uid = portal.organisation_module.getUid(),
                                            corporate_registration_code = \
                                    request_eform.getEstablishmentModification() \
                                    and request_eform.getEstablishmentCorporateRegistrationCode()\
                                    or request_eform.getCompanyCorporateRegistrationCode(),
                                            ignore_empty_string = 0)
  if not len(organisation_list):
    raise ValidationFailed('Organisation was not found for this person')
