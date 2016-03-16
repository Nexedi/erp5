from Products.ERP5Form.Report import ReportSection
result=[]
result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Support Requests'),
              form_id='SupportRequestModule_viewSupportRequestStatusList'))

result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Events'),
              form_id='SupportRequestModule_viewSupportRequestDetailedEventsList'))
return result
