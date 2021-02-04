# coding: utf-8
"""
Alarm must define a script that returns a list of dictionnaries with the following keys:

 - form_id str: id of an ERP5 Form or ERP5 Report. Required.
 - context erp5.portal_type.Base: the context to render the report. Required.
 - parameters dict: request parameters to render the report. Required.
   Must be serializable for CMFActivity
 - skin_name str: skin selection to use for this report ('ODS' | 'ODT'). Required.
 - format Optional[str]: convert the document to this format. Note that in scenarios like
   storing the result report in document module, it's better to keep the default format (None)
   and convert on demand the stored document.
 - language str: Localizer language to use. Required.
 - setup Callable[[dict], dict]: a function to call at setup before rendering the report.
   This function receive this dict as argument and must return a dict of the same type.
 - done Callable[[str, list[dict]], None]: a function called at the end of report production.
   This function receive two arguments, similar to ERP5Site_notifyReportComplete
      - subject str: the name of the report
      - attachment_list dict: files produced by the report, dicts with following keys:
         - name str: file name
         - mime str: file mime type
         - content bytes: file body

Note that this script will be called multiple times: A first time to decide which reports have
to be produced and when reports are finished, once for each report, to get the `done` callback.
"""

priority = 3
portal = context.getPortalObject()
report_configuration_script_id = context.getProperty('report_configuration_script_id')
assert report_configuration_script_id

for idx, report_data in enumerate(getattr(context, report_configuration_script_id)()):
  notify_report_complete_kwargs = {'idx': idx}
  if report_data.get('setup'):
    report_data = report_data['setup'](report_data)

  report_context = report_data.get('context', context)
  report_active_context = report_context.activate(
      activity='SQLQueue',
      node=portal.portal_preferences.getPreferredDeferredReportActivityFamily(),
      tag=tag,
      priority=priority,
  )

  if getattr(getattr(report_context, report_data['form_id']), 'pt', 'form_list') == 'form_report':
    # erp5 report
    report_active_context.Base_computeReportSection(
        form=report_data['form_id'],
        request_other=report_data['parameters'],
        user_name=None,
        tag=tag,
        skin_name=report_data['skin_name'],
        format=report_data.get('format', None),
        priority=priority,
        localizer_language=report_data['language'],
        notify_report_complete_script_id='Alarm_finalizeReportDocumentGeneration',
        notify_report_complete_kwargs=notify_report_complete_kwargs,
    )
  else:
    # simple view
    params = {}
    if 'format' in report_data:
      params['format'] = report_data['format']
    report_active_context.Base_renderSimpleView(
        localizer_language=report_data['language'],
        skin_name=report_data['skin_name'],
        request_form=report_data['parameters'],
        deferred_style_dialog_method=report_data['form_id'],
        user_name=None,
        params=params,
        notify_report_complete_script_id='Alarm_finalizeReportDocumentGeneration',
        notify_report_complete_kwargs=notify_report_complete_kwargs,
    )
