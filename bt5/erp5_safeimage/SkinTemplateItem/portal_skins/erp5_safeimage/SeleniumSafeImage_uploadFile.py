#from Products.ERP5.Document.TileImageTransformed import TileImageTransformed
#from six.moves import cStringIO as StringIO


portal = context.getPortalObject()


data = portal.restrictedTraverse("portal_skins/erp5_safeimage/img/image_test.jpg")

print(data.data)

return printed
