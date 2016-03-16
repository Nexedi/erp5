from Products.ERP5Form.Report import ReportSection
result=[]
result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Meetings'),
              form_id='MeetingModule_viewMeetingStatusList'))

result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Events'),
              form_id='MeetingModule_viewMeetingDetailedEventsList'))
return result
