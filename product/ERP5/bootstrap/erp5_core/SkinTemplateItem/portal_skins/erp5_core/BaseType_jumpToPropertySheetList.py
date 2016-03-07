portal = context.getPortalObject()
translateString = portal.Base_translateString

property_sheet_value_list = context.getRecursivePropertySheetValueList()
if not len(property_sheet_value_list):
  return context.Base_redirect(
    'view',
    keep_items={'portal_status_message':
                translateString('No ${portal_type} related.',
                                mapping={'portal_type': 'Property Sheet'})})

elif len(property_sheet_value_list) == 1:
  property_sheet = property_sheet_value_list[0]
  return property_sheet.Base_redirect(
    'view',
    keep_items={'portal_status_message':
                translateString('${this_portal_type} related to ${that_portal_type}: ${that_title}.',
                                mapping={'this_portal_type': 'Property Sheet',
                                'that_portal_type': context.getPortalType(),
                                'that_title': context.getTitleOrId()})})

property_sheet_uid_list = [property_sheet.getUid()
                           for property_sheet in property_sheet_value_list]

return portal.portal_property_sheets.Base_redirect(
  'view',
  keep_items={'reset': 1,
              'ignore_hide_rows': 1,
              'uid': property_sheet_uid_list})
