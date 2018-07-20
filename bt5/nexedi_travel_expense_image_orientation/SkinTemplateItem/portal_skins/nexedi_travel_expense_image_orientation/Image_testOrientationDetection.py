import StringIO

data = context.getData()
data = StringIO.StringIO(data)

return context.Base_detectImageOrientation(image=data)
