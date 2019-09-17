context.updateContentFromURL(repeat=repeat, crawling_depth=crawling_depth)
message = context.Base_translateString('Update started.')
return context.Base_redirect(form_id, keep_items=dict(portal_status_message=message))
