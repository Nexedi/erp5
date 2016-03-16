from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
request = portal.REQUEST

portal.portal_selections.setSelectionStats(selection_name, [], REQUEST=request)
portal.portal_selections.setSelectionColumns(selection_name, [], REQUEST=request)

return context.Base_redirect(form_id, keep_items=dict(
  portal_status_message=translateString("List Setting Reseted.")))
