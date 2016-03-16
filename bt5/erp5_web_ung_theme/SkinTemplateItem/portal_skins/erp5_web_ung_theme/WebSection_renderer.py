"""
  Redirect connected user to UNG Web Site or to document using the key 
"""
portal = context.getPortalObject()

request = context.REQUEST

if request.form.has_key("key"):
  webpage = context.ERP5Site_userFollowUpWebPage(reference=context.REQUEST.form.get("key"))
  webpage_id = webpage.getId()
  return context.Base_redirect("/web_page_module/%s" % webpage_id,
                              keep_items=dict(editable_mode=1))

else:
  portal_type_list = request.form.get("portal_type")
  searchable_text = request.form.get("SearchableText")
  return context.Base_redirect("unfoldDomain", 
                               keep_items = dict(unfoldDomain="ung_domain/all_documents.0",
                                                 form_id="erp5_web_ung_layout",
                                                 list_selection_name="ung_document_list_selection",
                                                 SearchableText=searchable_text,
                                                 portal_type=portal_type_list))
