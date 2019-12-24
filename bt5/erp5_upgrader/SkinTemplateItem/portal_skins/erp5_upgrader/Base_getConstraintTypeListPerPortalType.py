portal = context.getPortalObject()
constraint_type_list = portal.getPortalConstraintTypeList()

property_sheet_by_type_dict = {}
for portal_type in portal.portal_types.objectValues():
  property_sheet_list = portal_type.getTypePropertySheetList()
  if not property_sheet_list:
    continue
  for property_sheet in property_sheet_list:
    property_sheet_by_type_dict.setdefault(
      property_sheet, []).append(portal_type.getId())

type_per_constraint_type = {}
constraint_type_per_id = {}
for property_sheet in portal.portal_property_sheets.objectValues():
  constraint_list = property_sheet.objectValues(
    portal_type=constraint_type_list)
  if not constraint_list:
    continue
  type_list = []
  type_list_append = type_list.append
  property_sheet_id = property_sheet.getId()
  for constraint in constraint_list:
    method = getattr(constraint, 'getConstraintType', None)
    if not method:
      continue
    constraint_type = method()
    if constraint_type:
      if property_sheet_id in property_sheet_by_type_dict:
        type_per_constraint_type.setdefault(
          constraint_type, set()).update(
            property_sheet_by_type_dict[property_sheet_id])
      type_list_append(constraint_type)
  if type_list:
    constraint_type_per_id.setdefault(property_sheet_id, []).extend(type_list)

constraint_type_per_type = {}
for property_sheet_id, category_list in constraint_type_per_id.iteritems():
  for portal_type in property_sheet_by_type_dict.get(property_sheet_id, []):
    constraint_type_per_type.setdefault(portal_type, set()).update(category_list)

portal_type_tool = portal.portal_types

for portal_type in list(constraint_type_per_type.keys()):
  allowed_content_type_list = \
    portal_type_tool[portal_type].getTypeAllowedContentTypeList()
  for allowed_content_type in allowed_content_type_list:
    if allowed_content_type in constraint_type_per_type:
      type_list = constraint_type_per_type.pop(allowed_content_type)
      for constraint_type in type_list:
        type_per_constraint_type[constraint_type].remove(allowed_content_type)

return constraint_type_per_type, type_per_constraint_type
