attachement_method = getattr(context, 'PDFDocument_getApplicationIncomeDict')
attachement_type_dict = attachement_method()

type_list = map(lambda x: x.getId(), context.allowedContentTypes())
viewable_content_list = context.contentValues(portal_type=type_list, checked_permission='View')

content_title_list = []
for content in viewable_content_list:
  content_title_list.append(content.getTitle())

requirement = 0

for title in attachement_type_dict.keys():
  if attachement_type_dict[title]['requirement'] == 'Required':
    if title not in content_title_list:
      requirement = requirement + 1

return requirement
