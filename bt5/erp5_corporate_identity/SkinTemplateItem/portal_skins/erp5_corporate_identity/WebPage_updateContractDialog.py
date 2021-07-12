from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  return context.Base_redirect(
    dialog_id,
    keep_items = dict(
      portal_status_message=translateString('Preview updated.'),
      cancel_url=cancel_url,
      portal_skin=portal_skin,
      format=format,
      display_svg=display_svg,
      document_save=document_save,
      include_content_table=include_content_table,
      include_history_table=include_history_table,
      include_reference_table=include_reference_table,
      include_linked_content=include_linked_content,
      include_report_content=include_report_content,
      #**kw
    )
  )
