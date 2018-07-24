import StringIO

data = context.getData()
image = StringIO.StringIO(data)

image_oriented = context.Base_rotateImage(image=image, rotation=degree)

context.setData(image_oriented.getvalue())

old_orientation = context.getProperty("rotation", 0)
new_orientation = (old_orientation + degree) % 360
context.edit(rotation=new_orientation)

return ""
