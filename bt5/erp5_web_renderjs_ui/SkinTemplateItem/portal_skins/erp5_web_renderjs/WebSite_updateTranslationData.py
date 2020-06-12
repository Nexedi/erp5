from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

gadget_translation_data_js = context.WebSite_getTranslationDataWebScriptValue()
if gadget_translation_data_js is None:
  return context.Base_redirect(
      form_id,
      keep_items=dict(
          portal_status_message=translateString("No translation data script.")))

gadget_translation_data_js.setTextContent(
    context.WebSite_getTranslationDataTextContent())
portal.portal_workflow.doActionFor(
    gadget_translation_data_js,
    'edit_action',
    comment=translateString(
        "Translation data updated from web site ${web_site_id}.",
        mapping={'web_site_id': context.getId()}))

# Edit web section modification date
portal.portal_workflow.doActionFor(
    context,
    'edit_action',
    comment=translateString("Translation data updated.",))

if REQUEST is not None:
  return context.Base_redirect(
      form_id,
      keep_items=dict(
          portal_status_message=translateString("Translation data updated.")))
