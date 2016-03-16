"""
  This script resets security on all forms after validation by registry officer
"""

portal = context.getPortalObject()
request_eform = state_change['object']
N_ = portal.Base_translateString

new_reference = request_eform.getRegistrationNumber()

sql_kw = {}
sql_kw['portal_type'] = 'Assignment'
sql_kw['validation_state'] = 'open'
sql_kw['default_destination_uid'] = request_eform.getUid()
sql_kw['default_function_uid'] = request_eform.portal_categories.function.entreprise.getUid()
for assignment in request_eform.portal_catalog(**sql_kw):
  assignment.setCorporateRegistrationCode(new_reference)

# We need to update security now
request_eform.updateLocalRolesOnSecurityGroups()
