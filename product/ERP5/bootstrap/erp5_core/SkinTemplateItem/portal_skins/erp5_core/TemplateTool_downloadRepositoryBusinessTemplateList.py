REQUEST = container.REQUEST
RESPONSE = REQUEST.RESPONSE

selection_name = kw['list_selection_name']
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)

ret_url = '/'.join([context.absolute_url(), REQUEST.get('form_id', 'view')])

if len(uids) == 0:
  RESPONSE.redirect("%s?portal_status_message=No+Business+Template+Specified" % ret_url)
  return

id_list = []
for uid in uids:
  repository, id_ = context.decodeRepositoryBusinessTemplateUid(uid)
  bt = context.download('/'.join([repository, id_]))
  id_list.append(bt.getId())

RESPONSE.redirect("%s?portal_status_message=Business+Templates+Downloaded+As:+%s" % (ret_url, ',+'.join(id_list)))
