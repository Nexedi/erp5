portal = context.getPortalObject()
translateString = portal.Base_translateString

# XXX: Merge with BaseType_jumpToPropertySheetList
value_list = context.getRecursivePortalTypeValueList()
if not len(value_list):
  return context.Base_redirect(
    'view',
    keep_items={'portal_status_message':
                translateString('No ${portal_type} related.',
                                mapping={'portal_type': 'Portal Type'})})

elif len(value_list) == 1:
  value = value_list[0]
  return value.Base_redirect(
    'view',
    keep_items={'portal_status_message':
                translateString('${this_portal_type} related to ${that_portal_type}: ${that_title}.',
                                mapping={'this_portal_type': 'Portal Type',
                                'that_portal_type': context.getPortalType(),
                                'that_title': context.getTitleOrId()})})

return portal.portal_types.Base_redirect(
  'view',
  keep_items={'reset': 1,
              'ignore_hide_rows': 1,
              'uid': [value.getUid() for value in value_list]})
