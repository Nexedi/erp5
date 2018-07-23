import StringIO

data = context.getData()
image = StringIO.StringIO(data)

image_oriented = context.Base_rotateImage(image=image, rotation=rotation)

context.setData(image_oriented.getvalue())

actual_orientation = context.getProperty("orientation", 0)
new_orientation = (actual_orientation + rotation) % 360
context.edit(orientation=new_orientation)

return ""
