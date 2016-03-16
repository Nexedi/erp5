box_relative_url = context.REQUEST.get('box_relative_url', None)
box = context.restrictedTraverse(box_relative_url)
preferences = box.KnowledgeBox_getDefaultPreferencesDict()
preferred_tag = preferences.get('preferred_tag', None)
if preferred_tag is not None:
  subject_list_from_preferences=[x for x in preferred_tag.split(' ') if x!='']
  if subject_list_from_preferences:
    return context.portal_catalog(subject=["%%%s%%" %tag for tag in subject_list_from_preferences])
return []
