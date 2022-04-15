# pylint: disable=redefined-builtin
portal = context.getPortalObject()
if notify_report_complete_kwargs is None:
  notify_report_complete_kwargs = {}

form = context.restrictedTraverse(form)
request = container.REQUEST
request.form.update(report_request)
request.other.update(report_request)

with portal.Localizer.translationContext(localizer_language):
  if form.meta_type == 'ERP5 Report':
    report_section_list = getattr(context, form.report_method)()
  elif form.meta_type == 'ERP5 Form':
    report_section_list = []
    for field in form.get_fields():
      if field.getRecursiveTemplateField().meta_type == 'ReportBox':
        report_section_list.extend(field.render())
  else:
    raise ValueError('form meta_type (%r) unknown' %(form.meta_type,))

  report_title = portal.Base_translateString((form.getProperty('title')))

# Rebuild request as report section can have modified request content
report_request = portal.ERP5Site_filterRequestForDeferredStyle(request)

active_process = portal.portal_activities.newActiveProcess()
inner_tag = tag + '-render'

for idx, report_section in enumerate(report_section_list):
  if report_section.getPath():
    doc = report_section.getObject(portal)
  else:
    doc = context
  doc.activate(activity='SQLQueue',
               node=portal.portal_preferences.getPreferredDeferredReportActivityFamily(),
               active_process=active_process,
               tag=inner_tag,
               priority=priority,
              ).Base_renderReportSection(skin_name=skin_name,
                                         localizer_language=localizer_language,
                                         report_section=report_section,
                                         report_section_idx=idx,
                                         report_request=report_request,
                                         )

activity_context = context
if activity_context == portal:
  # portal is not an active object
  activity_context = portal.portal_simulation

activity_context.activate(
    activity='SQLQueue',
    node=portal.portal_preferences.getPreferredDeferredReportActivityFamily(),
    after_tag=inner_tag,
    tag=tag,
    priority=priority,
).Base_report(
           active_process_url=active_process.getRelativeUrl(),
           skin_name=skin_name,
           localizer_language=localizer_language,
           title=report_title,
           report_request=report_request,
           form_path=form.getPhysicalPath(),
           user_name=user_name,
           format=format,
           report_section_count=len(report_section_list),
           notify_report_complete_script_id=notify_report_complete_script_id,
           notify_report_complete_kwargs=notify_report_complete_kwargs,
)
