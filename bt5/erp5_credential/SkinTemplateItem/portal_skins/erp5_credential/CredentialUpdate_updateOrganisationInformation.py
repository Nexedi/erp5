"""Copy subscription information to related person"""

organisation = context.getDestinationDecisionValue(portal_type="Organisation")

#Mapping
organisation_mapping = (
    # (subscription, organisation)
    ('default_email_coordinate_text', 'default_email_coordinate_text'),
    ('default_telephone_text', 'default_telephone_text'),
    ('default_fax_text', 'default_fax_text'),
    ('default_address_street_address', 'default_address_street_address'),
    ('default_address_zip_code', 'default_address_zip_code'),
    ('default_address_city', 'default_address_city'),
    ('default_address_region', 'default_address_region'),
    ('default_mobile_telephone_text', 'default_mobile_telephone_text'),
    ('activity_list', 'activity_list'),
    ('description', 'description'),
    )

context.Credential_copyRegistredInformation(organisation, organisation_mapping)

#Update the logo
context.CredentialUpdate_copyDefaultImage()
