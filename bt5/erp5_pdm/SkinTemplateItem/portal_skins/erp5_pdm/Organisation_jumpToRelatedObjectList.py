"""
Jump from Organisation to its related objects (but only if used as
source* or destination* categories) of the same portal type and
displayed using the module view
"""
portal = context.getPortalObject()

# XXX: Seems there is no other better way to get the Arrow
#      destination/section categories...
base_category_uid_list = []
for arrow_property in portal.portal_property_sheets.Arrow.contentValues():
  if arrow_property.getPortalType() != 'Category Property':
    continue

  arrow_property_title = arrow_property.getTitle()
  if (arrow_property_title.startswith('source') or
      arrow_property_title.startswith('destination')):
    base_category_uid_list.append(portal.portal_categories[arrow_property_title].getUid())

related_object_list = context.getPortalObject().portal_catalog(
    portal_type=portal_type,
    **{
        'category.category_uid': context.getUid(),
        'category.base_category_uid': base_category_uid_list,
    }
)

if not related_object_list:
  return context.Base_redirect(form_id, keep_items=dict(
    portal_status_message=portal.Base_translateString(
    'No %s Related' % portal_type,
    default=portal.Base_translateString('No ${portal_type} related.',
                             mapping={'portal_type': portal.Base_translateString(portal_type)}))))

elif len(related_object_list) == 1:
  related_object = related_object_list[0]
  return related_object.Base_redirect(keep_items=dict(
      reset=1,
      portal_status_message=portal.Base_translateString(
      # first, try to get a full translated message with portal types
      "%s related to %s." % (related_object.getPortalType(), context.getPortalType()),
       # if not found, fallback to generic translation
      default=portal.Base_translateString('${this_portal_type} related to ${that_portal_type} : ${that_title}.',
        mapping={"this_portal_type": related_object.getTranslatedPortalType(),
                 "that_portal_type": context.getTranslatedPortalType(),
                 "that_title": context.getTitleOrId()}))))

else:
  message = portal.Base_translateString(
  # first, try to get a full translated message with portal types
  "Documents related to %s." % context.getPortalType(),
  # if not found, fallback to generic translation
  default=portal.Base_translateString('Documents related to ${that_portal_type} : ${that_title}.',
        mapping={"that_portal_type": context.getTranslatedPortalType(),
                 "that_title": context.getTitleOrId() }),)
  # XXX: Use POST rather than GET because of GET URL length limitation?
  return portal.getDefaultModule(portal_type).Base_redirect(
    keep_items={'reset': 1,
                'portal_status_message': message,
                'uid': [obj.uid for obj in related_object_list]})
