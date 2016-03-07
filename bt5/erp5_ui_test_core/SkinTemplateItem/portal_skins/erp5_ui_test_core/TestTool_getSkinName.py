portal = context.getPortalObject()
return portal.getSkinNameFromRequest(context.REQUEST) or \
    portal.portal_skins.getDefaultSkin()
