"""
================================================================================
Update a book report dialog with parameters manually entered
================================================================================
"""
from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  return context.Base_redirect(
    dialog_id,
    keep_items = dict(
      portal_status_message=translateString('Preview updated.'),
      cancel_url=cancel_url,
      portal_skin=portal_skin,
      format=format,
      document_save=document_save,
      document_download=document_download,
      document_language=document_language,
      document_reference=document_reference,
      document_version=document_version,
      document_title=document_title,
      display_depth=display_depth,
      display_detail=display_detail,
      display_comment=display_comment,
      display_header=display_header,
      report_name=report_name,
      report_title=report_title,
      requirement_relative_url=requirement_relative_url,
      **kw
    )
  )
