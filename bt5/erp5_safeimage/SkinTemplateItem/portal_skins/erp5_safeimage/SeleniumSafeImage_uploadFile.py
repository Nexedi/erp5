portal = context.getPortalObject()
data = portal.restrictedTraverse("portal_skins/erp5_safeimage/img/image_test.jpg")
print(data.data)
return printed
