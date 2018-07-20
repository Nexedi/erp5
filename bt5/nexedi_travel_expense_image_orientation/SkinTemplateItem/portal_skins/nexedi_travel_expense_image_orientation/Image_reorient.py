import StringIO

data = context.getData()
image = StringIO.StringIO(data)

image_oriented = context.Base_reorientImage(image=image)

context.setData(image_oriented.getvalue())

return "ok"
