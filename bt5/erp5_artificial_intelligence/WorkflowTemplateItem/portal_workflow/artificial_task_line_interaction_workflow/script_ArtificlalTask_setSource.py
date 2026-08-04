document = state_change['object']
source_list = document.getSourceValueList()
person = document.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if person is not None and person not in source_list:
  source_list.append(person)
  document.setSourceValueList(source_list)
