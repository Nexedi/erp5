portal = context.getPortalObject()

user = portal.portal_catalog.getResultValue(portal_type="Person", reference="test_user")

return user is not None
