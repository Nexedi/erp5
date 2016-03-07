from Products.ERP5Type.Utils import convertToUpperCase
related_person_list = []
known_person_uid = {}

for base_category in ['natural_parent', 'legal_parent', 'insurance_coverage'] :
  relation_title = context.getPortalObject().portal_categories[base_category].getTranslatedTitle()
  relation_method = getattr(context, "get%sRelatedValueList" % convertToUpperCase(base_category))
  for person in relation_method( portal_type = 'Person' ) :
    if person.getUid() not in known_person_uid :
      known_person_uid[person.getUid()] = 1
      related_person_list.append(person.asContext(relation_title = relation_title))

return related_person_list
