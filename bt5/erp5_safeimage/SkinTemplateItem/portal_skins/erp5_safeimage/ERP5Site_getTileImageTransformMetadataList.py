import json

context.REQUEST.response.setHeader('Access-Control-Allow-Origin', '*')
data = {}
data["image_list"] = []
image_list = data["image_list"]
for tile_image in context.portal_catalog(portal_type="Image Tile Transformed"):
  title = tile_image.getTitle()
  id =  tile_image.getId()
  image_list.append({"title":title, "id": id})

return json.dumps(data)
