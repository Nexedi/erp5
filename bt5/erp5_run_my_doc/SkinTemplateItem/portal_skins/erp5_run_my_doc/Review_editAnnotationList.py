annotation_list = context.getAnnotation().split('\n')
user_name = context.getPortalObject().portal_membership.getAuthenticatedMember().getId()
for uid in listbox_uid:
  i = int(uid)
  old_comment, locator, context_url, author, color = annotation_list[i][1:-1].split("},{")
  new_comment = context.REQUEST['field_listbox_title_' + uid]
  #print('Old title: ' + old_comment + ' -> ' + new_comment)
  if old_comment != new_comment:
    author = user_name
    annotation_list[i] = "{" + str(new_comment) + "},{" + str(locator) + "},{" + str(context_url) + "},{" + str(author) + "},{" + str(color) + '}'
    annotation_list[i] = annotation_list[i]

context.setAnnotation("\n".join(annotation_list))

translateString = context.Base_translateString
portal_status_message = translateString('Data updated.')
context.Base_redirect('Review_viewAnnotationList', keep_items = dict(portal_status_message=portal_status_message))
