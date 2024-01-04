import json
portal = context.getPortalObject()
context.REQUEST.response.setHeader('Access-Control-Allow-Origin', '*')
print(portal.portal_catalog(portal_type="Image Title", src__=1))
#return printed
data = {}
data["image_list"] = []
image_list = data["image_list"]
for tile_image in portal.portal_catalog(portal_type="Image Tile"):
  title = tile_image.getTitle()
  id =  tile_image.getId()
  image_list.append({"title":title, "id": id})

return json.dumps(data)
