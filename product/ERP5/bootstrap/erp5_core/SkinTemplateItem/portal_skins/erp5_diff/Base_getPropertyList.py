from Products.ERP5Type.Document import newTempBase

portal = context.getPortalObject()
result = []

for key, val in context.propertyItems():

  if val:
    temp_obj = newTempBase(context, '')
    temp_obj.setProperty('name', key)
    temp_obj.setProperty('current_value', val)
    result.append(temp_obj)

result.sort(key=lambda x: x.getProperty('name'))
return result
