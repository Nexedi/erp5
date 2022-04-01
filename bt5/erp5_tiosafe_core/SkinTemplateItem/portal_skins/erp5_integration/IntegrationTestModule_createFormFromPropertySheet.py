# This script is intented to be called on a form

ps = context.getPortalObject().portal_property_sheets[property_sheet_id]

for prop in ps.objectValues(portal_type="Standard Property"):
  field_id = "my_%s" %prop.getReference()
  if getattr(context, field_id, None) is None:
    print("will add %s" %(field_id))
    if prop.getElementaryType() == "string":
      context.manage_addField(field_id, prop.getReference(), "StringField")
    elif prop.getElementaryType() == "boolean":
      context.manage_addField(field_id, prop.getReference(), "CheckBoxField")
    else:
      print("unkown type", prop.getElementaryType())

return printed
