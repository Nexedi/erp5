"""
  Add contributor to document if logged in user has a respective ERP5
  Person object.
"""
document = state_change['object']
contributor_list = document.getContributorValueList()
person = document.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if person is not None and person not in contributor_list:
  # a real ERP5 Person object does exist
  contributor_list.append(person)
  document.setContributorValueList(contributor_list)
