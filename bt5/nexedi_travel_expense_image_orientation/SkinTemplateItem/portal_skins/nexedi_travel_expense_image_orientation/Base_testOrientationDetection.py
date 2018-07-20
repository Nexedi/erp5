import StringIO

data = context.getPortalObject().image_module['7656'].getData()
data = StringIO.StringIO(data)

return context.OrientationDetection_orientation(image=data)
