dms_module = getattr(context, 'document_module', None)
attachment_info_list =  context.getAttachmentInformationList()
Base_translateString = context.Base_translateString
if dms_module is not None:
  for uid in uids:
    # Maybe select Line can be improved later
    line = [ l for l in listbox if l['listbox_key'].split('/')[-1] ==  uid][0]
    # index is numeric and comes with uid
    attachment_index = int(uid.split('index_')[-1])
    attachment_info = [i for i in attachment_info_list if i['index'] == attachment_index][0]
    file_ = context.getAttachmentData(index=attachment_index)
    document = dms_module.newContent(follow_up=context.getFollowUp(),
                                     portal_type = line['content_type'],
                                     description = line['description'],
                                     version = line['version'],
                                     short_title = line['short_title'],
                                     language = line['language'],
                                     reference= line['reference'],
                                     title = line['title'])
    document.edit(source_reference=attachment_info['file_name'], file=file_)

if len(uids) == 1:
  message = Base_translateString('${portal_type} created successfully.',
                                 mapping={'portal_type':document.getTranslatedPortalType()})
  return document.Base_redirect(keep_items=dict(portal_status_message=message))

message = Base_translateString('${count} documents created successfully.',
                               mapping={'count':len(uids)})

return context.Base_redirect(keep_items=dict(portal_status_message=message))
