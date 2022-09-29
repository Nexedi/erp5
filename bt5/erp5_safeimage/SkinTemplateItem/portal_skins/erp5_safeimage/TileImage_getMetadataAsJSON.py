import json

context.REQUEST.response.setHeader('Access-Control-Allow-Origin', '*')
tile_image = context
xml_file = tile_image["ImageProperties.xml"]
xml_split = xml_file.getData().split(" ")
widthpre = xml_split[1].split("=")
heightpre = xml_split[2].split("=")
width = widthpre[1][1:-1]
height = heightpre[1][1:-1]
data = {}
data["sizes"] = []
sizes = data["sizes"]
sizes.append({"width":width,"height":height})

return json.dumps(data)
