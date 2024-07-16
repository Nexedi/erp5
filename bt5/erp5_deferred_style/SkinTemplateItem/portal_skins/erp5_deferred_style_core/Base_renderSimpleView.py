# Render a "normal" form or an OOo template in an activity and send it by email
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
if notify_report_complete_kwargs is None:
  notify_report_complete_kwargs = {}
request = portal.REQUEST
report_format = request_form.get('format', '')
if portal.portal_preferences.getPreferredDeferredReportStoredAsDocument():
  request_form['format'] = None

request.form.update(request_form)

if skin_name and skin_name != 'None': # make_query serializes None as 'None'
  portal.portal_skins.changeSkin(skin_name)

with portal.Localizer.translationContext(localizer_language):
  report_data = getattr(context, deferred_style_dialog_method)(**params)

  attachment_name_list = [x[len(' filename='):] for x in (request.RESPONSE.getHeader(
                        'content-disposition') or '').split(';')
                            if x.startswith(' filename=')]
  if attachment_name_list:
    attachment_name, = attachment_name_list
  else:
    assert 'inline' in (request.RESPONSE.getHeader('content-disposition') or '')
    attachment_name = 'index.html'
  if attachment_name.startswith('"'):
    attachment_name = attachment_name[1:]
  if attachment_name.endswith('"'):
    attachment_name = attachment_name[:-1]
  attachment_list = (
    {'mime_type': (request.RESPONSE.getHeader('content-type') or 'application/octet-stream;').split(';')[0],
     'content': bytes(report_data),
     'name': attachment_name},)

  getattr(portal, notify_report_complete_script_id)(
    user_name=user_name,
    subject=str(translateString(attachment_name.rsplit('.', 1)[0])),
    message='',
    attachment_list=attachment_list,
    format=report_format,
    **notify_report_complete_kwargs
  )
