from Products.ERP5Type.Message import translateString

portal = context.getPortalObject()
comment = portal.comment_module.newContent(portal_type="Comment",
                   text_content=text_content,
                   comment_type=comment_type,
                   follow_up=context.getRelativeUrl(),
                   source_value=portal.ERP5Site_getAuthenticatedMemberPersonValue(),
                   effective_date=DateTime())
if batch_mode is False:
  return context.Base_redirect(form_id,
      keep_items=dict(portal_status_message=translateString('Comment added.')))
return comment
