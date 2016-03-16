"""External Validator for SubscriptionForm_view/my_company_name
checks that there no company already registered with this login.
"""
return len(context.portal_catalog(portal_type='Organisation',
    corporate_registration_code=editor))
