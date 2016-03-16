from Products.ERP5Form.Report import ReportSection
result=[]
result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Campaigns'),
              form_id='CampaignModule_viewCampaignStatusList'))

return result
