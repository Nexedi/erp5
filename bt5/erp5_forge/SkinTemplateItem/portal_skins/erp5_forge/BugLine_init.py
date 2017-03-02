# Set preferred text format
portal = context.getPortalObject()
edit_kw = {'content_type': portal.portal_preferences.getPreferredTextFormat(),
           'start_date': DateTime(),
           'destination_value_list': context.BugLine_getRecipientValueList()}

# Define a Reporter as Source Trade
person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if person is not None:
  edit_kw['source_value'] = person

context.edit(**edit_kw)
