from Products.ERP5Type.Message import translateString

request = container.REQUEST
request.other.update(request_other)

portal = context.getPortalObject()
ap = portal.restrictedTraverse(active_process_url)

with portal.Localizer.translationContext(localizer_language):
  # set the selected skin
  portal.portal_skins.changeSkin(skin_name)

  report_section_list = [r.getResult() for r in ap.getResultList()]
  assert len(report_section_list) == report_section_count
  report_section_list.sort(key=lambda x: x[0])
  
  def dummyReportMethod():
    return report_section_list

  def decodeReportSection(data):
    # BBB We use to encode in zlib
    try:
      return data.decode('bz2')
    except IOError:
      return data.decode('zlib')

  report_data = context.restrictedTraverse(form_path).report_view.pt_render(
      extra_context=dict(options={'format': format},
                         rendered_report_item_list=(decodeReportSection(r[1]) for r in report_section_list),
                         report_method=dummyReportMethod,
                         form=portal.restrictedTraverse(form_path)))

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
     'content': '%s' % report_data,
     'name': attachment_name},)

portal.ERP5Site_notifyReportComplete(
  user_name=user_name,
  subject=title,
  message='',
  attachment_list=attachment_list)
