context.updateVariationCategoryList()
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

message = Base_translateString('%s Updated.' % context.getPortalType())
return context.Base_redirect(form_id=form_id,
                      selection_name=selection_name,
                      selection_index=selection_index,
                      keep_items={'portal_status_message': message})
