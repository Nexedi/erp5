"""
XXX (rafael) I believe KM has a much better way to do this,
 clone web page, maybe using Base_createCloneDocument from erp5_base
"""

conv_obj_module = context.getDefaultModule(conv_obj_type)
counter = 0
for uid in uids:
  counter += 1
  obj = context.portal_catalog.getResultValue(uid=uid)
  conv_obj = conv_obj_module.newContent(portal_type = conv_obj_type,
                                        title = obj.getTitle(),
                                        short_title = obj.getShortTitle(),
                                        reference = obj.getReference(),
                                        int_index = obj.getIntIndex(),
                                        version = obj.getVersion(),
                                        language = obj.getLanguage(),
                                        effective_date = obj.getEffectiveDate(),
                                        description = obj.getDescription(),
                                        publication_section_list = obj.getPublicationSectionList(),
                                        text_content = obj.getTextContent(),
                                        format = obj.getFormat(),
                                        contributor_list = obj.getContributorList())

  conv_obj = conv_obj.manage_pasteObjects(
                         obj.manage_copyObjects(list(obj.objectIds())))

return conv_obj_module.Base_redirect('',
    dict(portal_status_message=context.Base_translateString(
        "${document_count} documents converted.",
        mapping={'document_count': counter})))
