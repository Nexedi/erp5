portal_type_dict = {"Web Page": ["Text", "web_page_template"],
                    "Web Table": ["Spreadsheet", "web_table_template"],
                    "Web Illustration": ["Drawing", "web_illustration_template"]}

portal_type = context.REQUEST.form.get("portal_type")
document = context.Base_contribute(file=file, 
                       url=None, 
                       portal_type=portal_type_dict.get(portal_type)[0], 
                       synchronous_metadata_discovery=None, 
                       redirect_to_document=False, 
                       attach_document_to_context=False, 
                       use_context_for_container=False, 
                       redirect_url=None, 
                       cancel_url=None, 
                       batch_mode=False,
                       max_repeat=0, 
                       editable_mode=1,
                       follow_up_list=None, 
)

return context.ERP5Site_createNewWebDocument(template=portal_type_dict.get(portal_type)[1],
                                             selection_action=portal_type,
                                             document_path=document.getPath(),
                                             upload_document=1)
