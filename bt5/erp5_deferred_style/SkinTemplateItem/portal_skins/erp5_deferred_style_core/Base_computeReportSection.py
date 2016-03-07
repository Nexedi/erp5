portal = context.getPortalObject()
N_ = portal.Base_translateString

form = context.restrictedTraverse(form)
request = container.REQUEST
request.other.update(request_other)

if form.meta_type == 'ERP5 Report':
  report_section_list = getattr(context, form.report_method)()
elif form.meta_type == 'ERP5 Form':
  report_section_list = []
  for field in form.get_fields():
    if field.getRecursiveTemplateField().meta_type == 'ReportBox':
      report_section_list.extend(field.render())
else:
  raise ValueError, 'form meta_type (%r) unknown' %(form.meta_type,)

# Rebuild request_other as report section can have modify request content
request_other = {}
for k, v in request.items():
  if k not in ('TraversalRequestNameStack', 'AUTHENTICATED_USER', 'URL',
      'SERVER_URL', 'AUTHENTICATION_PATH', 'USER_PREF_LANGUAGES', 'PARENTS',
      'PUBLISHED', 'AcceptLanguage', 'AcceptCharset', 'RESPONSE', 'SESSION',
      'ACTUAL_URL'):
    # XXX proxy fields stores a cache in request.other that cannot be pickled
    if same_type(k, '') and str(k).startswith('field__proxyfield'):
      continue
    # Remove FileUpload parameters
    elif getattr(v, 'headers', ''):
      continue
    request_other[k] = v

localizer_language = portal.Localizer.get_selected_language()
active_process = portal.portal_activities.newActiveProcess()

for idx, report_section in enumerate(report_section_list):
  if report_section.getPath():
    doc = report_section.getObject(portal)
  else:
    doc = context
  doc.activate(activity='SQLQueue',
               active_process=active_process,
               tag=tag,
               priority=priority,
              ).Base_renderReportSection(skin_name=skin_name,
                                         localizer_language=localizer_language,
                                         report_section=report_section,
                                         report_section_idx=idx,
                                         request_other=request_other)

activity_context = context
if activity_context == portal:
  # portal is not an active object
  activity_context = portal.portal_simulation

activity_context.activate(activity='SQLQueue', after_tag=tag, priority=priority).Base_report(
           active_process_url=active_process.getRelativeUrl(),
           skin_name=skin_name,
           localizer_language=localizer_language,
           title=N_(form.getProperty('title')),
           request_other=request_other,
           form_path=form.getPhysicalPath(),
           user_name=user_name,
           format=format,
           report_section_count=len(report_section_list)
          )
