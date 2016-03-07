from DateTime import DateTime
portal = context.getPortalObject()
person = state_change['object']

# check preferences and save only if set
number_of_last_password_to_check = portal.portal_preferences.getPreferredNumberOfLastPasswordToCheck()

if number_of_last_password_to_check is not None and number_of_last_password_to_check:
  # save password and modification date
  current_password = person.getPassword()
  if current_password is not None:
    password_event = portal.system_event_module.newContent(portal_type = 'Password Event',
                                                           source_value = person,
                                                           destination_value = person,
                                                           password = current_password)
    password_event.confirm()
    # Person_isPasswordExpired cache the wrong result if document is not in catalog.
    # As the document is created in the same transaction, it is possible to force reindexation
    password_event.immediateReindexObject()
