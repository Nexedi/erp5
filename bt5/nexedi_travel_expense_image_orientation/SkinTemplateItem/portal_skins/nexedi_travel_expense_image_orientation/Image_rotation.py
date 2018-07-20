import StringIO

data = context.getData()
image = StringIO.StringIO(data)

image_oriented = context.Base_rotateImage(image=image, rotation=rotation)

context.setData(image_oriented.getvalue())

return ""
