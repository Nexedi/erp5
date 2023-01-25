import json

context.REQUEST.response.setHeader('Access-Control-Allow-Origin', '*')
file = context["TransformFile.txt"].getData().split()
data = {}
data["transforms"]=[]
transforms=data["transforms"]
#Reverse Text File to improve performance in the browser
while(file):
 line = file[:6]
 transforms.append({"tilegroup":line[0],"tileid":line[1],"algorithm":line[2],"param1":line[3],"param2":line[4],"num":line[5]})
 del(file[:6])

return json.dumps(transforms)
