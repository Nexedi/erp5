from Products.ERP5Type.Errors import UnsupportedWorkflowMethod
"""Copy subscription information to the related organisation"""

context.Credential_checkConsistency(['Organisation'])
organisation = context.getDestinationDecisionValue(portal_type="Organisation")

#Mapping
organisation_mapping = (
    ('organisation_title', 'corporate_name'),
    ('organisation_description', 'description',),
    ('organisation_default_telephone_text', 'default_telephone_text'),
    ('organisation_default_address_street_address', 'default_address_street_address'),
    ('organisation_default_address_zip_code', 'default_address_zip_code'),
    ('organisation_default_address_city', 'default_address_city'),
    ('organisation_default_address_region', 'default_address_region'),
    )

context.Credential_copyRegistredInformation(organisation, organisation_mapping)

#Try to validate
try:
  organisation.validate()
except UnsupportedWorkflowMethod:
  pass
