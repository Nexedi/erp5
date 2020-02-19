request = container.REQUEST
request.other.update(request_other)

portal = context.getPortalObject()

with portal.Localizer.translationContext(localizer_language):
  portal.portal_skins.changeSkin(skin_name)

  # for unicode encoding
  request.RESPONSE.setHeader("Content-Type", "application/xml; charset=utf-8")
  render_prefix = 'x%s' % report_section_idx
  report_section.pushReport(portal, render_prefix=render_prefix)

  if report_section.getFormId():
    form = getattr(context, report_section.getFormId())
  else:
    form = None

  data = context.render_report_section.pt_render(
                extra_context=dict(form=form,
                                   first=report_section_idx == 0,
                                   report_section=report_section,
                                   render_prefix=render_prefix))

  report_section.popReport(portal, render_prefix=render_prefix)

return report_section_idx, data.encode('utf8').encode('bz2')
