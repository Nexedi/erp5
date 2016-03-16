"""Update relative entity with a credential update. Allow to update a organisation or a person for exemple"""
#Use list and getattr to do generic purpose
for destination_decision in context.getDestinationDecisionValueList():
  portal_type = destination_decision.getPortalType().replace(' ','')
  getattr(context,'CredentialUpdate_update%sInformation' % portal_type)()
