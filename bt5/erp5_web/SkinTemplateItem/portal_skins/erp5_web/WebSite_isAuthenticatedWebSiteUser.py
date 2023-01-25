"""
  Decide if current user is a Web Site User or Web Site Administrator.
  This check is typically useful for showing/hiding different
  parts of Web Site like Admin Toolbox or determining the appropriate
  'view' action on object.
"""

portal_membership = context.portal_membership
if portal_membership.isAnonymousUser() or portal_membership.getAuthenticatedMember().has_role(('Member',)):
  ## Anonymous/Member is likely to be an website visitor
  return True
else:
  return False
