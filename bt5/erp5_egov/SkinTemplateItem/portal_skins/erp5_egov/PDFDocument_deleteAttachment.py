request=context.REQUEST
portal = context.getPortalObject()
N_ = portal.Base_translateString

if id_list == None:
  message = N_("Please+select+one+or+more+items+to+delete+first.")
  qs = '?portal_status_message=%s' % message
  return request.RESPONSE.redirect( context.absolute_url() + '/' + form_id + qs )

if not same_type(id_list, []):
  id_list=[id_list,]

if len(id_list) >1:
  message = N_("Please+select+only+one+item+to+delete.")
  qs = '?portal_status_message=%s' % message
  return request.RESPONSE.redirect( context.absolute_url() + '/' + form_id + qs )

object = getattr(context, id_list[0], None)

portal.portal_workflow.doActionFor(object, 'delete_action')
message = N_('Attachment ${file_name} has been deleted', mapping = { 'file_name': '"%s"' % file_name})
qs = '?portal_status_message=%s' % message
return request.RESPONSE.redirect( context.absolute_url() + '/' + form_id + qs )
