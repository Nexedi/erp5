"""User opening the support request will be set a source.
"""
support_request = sci['object']
portal = support_request.getPortalObject()
user = portal.portal_membership.getAuthenticatedMember().getUserValue()
if user is not None and not support_request.getSource():
  support_request.setSourceValue(user)
