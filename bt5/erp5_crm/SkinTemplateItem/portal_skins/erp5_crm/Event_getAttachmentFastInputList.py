from Products.ERP5Type.Document import newTempBase
contribution_registry = context.portal_contribution_registry

base_list = []
for attachment in context.getAttachmentInformationList():
  # XXX this is for prevent get parts related to body or not related to
  # Attachments
  if attachment['uid'] not in ['part_1', 'part_0']:
    filename  = context.getTitle()
    if attachment.has_key("file_name"):
       filename=attachment["file_name"]
    pt = "File"
    temp_base_id = 'index_'.join([attachment["uid"], str(attachment["index"])])
    base_list.append(newTempBase(context, id=temp_base_id,
                                              uid=temp_base_id,
                                              index= attachment["index"],
                                              file_name=filename,
                                              content_type=pt))

return base_list
