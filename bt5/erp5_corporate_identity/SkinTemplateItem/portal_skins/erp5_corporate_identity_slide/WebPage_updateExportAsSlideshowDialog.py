"""
================================================================================
Update the slide dialog with parameters manually entered
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
      override_logo_reference=override_logo_reference,
      override_publisher_title=override_publisher_title,
      note_display=note_display,
      svg_display=svg_display,
      format=format,
    )
  )
