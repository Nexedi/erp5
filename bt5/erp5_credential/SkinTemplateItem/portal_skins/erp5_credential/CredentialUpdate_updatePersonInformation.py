"""Copy subscription information to related person"""

context.Credential_checkConsistency(['Person'])
person = context.getDestinationDecisionValue(portal_type="Person")

# Person Mapping
person_mapping = (
    # (credential, person)
    ('social_title', 'social_title'),
    ('first_name', 'first_name'),
    ('last_name', 'last_name'),
    ('gender', 'gender'),
    ('date_of_birth', 'birthday'),
    ('nationality', 'nationality'),
    ('language', 'language'),
    ('default_email_text', 'default_email_text'),
    ('default_telephone_telephone_country', 'default_telephone_telephone_country'),
    ('default_telephone_text', 'default_telephone_text'),
    ('default_fax_text', 'default_fax_text'),
    ('default_address_street_address', 'default_address_street_address'),
    ('default_address_zip_code', 'default_address_zip_code'),
    ('default_address_city', 'default_address_city'),
    ('default_address_region', 'default_address_region'),
    ('default_mobile_telephone_telephone_country', 'default_mobile_telephone_telephone_country'),
    ('default_mobile_telephone_text', 'default_mobile_telephone_text'),
    ('activity_list', 'default_career_activity_list'),
    ('function_list', 'default_career_function_list'),
    ('skill_list', 'default_career_skill_list'),
    ('default_credential_question_answer', 'default_credential_question_answer'),
    ('default_credential_question_question', 'default_credential_question_question'),
    ('default_credential_question_question_free_text', 'default_credential_question_question_free_text'),
    ('description', 'description'),
    )

context.Credential_copyRegistredInformation(person, person_mapping,copy_none_value=False)

context.Credential_updatePersonPassword()

#Update the photo
context.CredentialUpdate_copyDefaultImage()
