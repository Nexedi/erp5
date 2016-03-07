from Products.ERP5Form.Report import ReportSection
result=[]
result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Sale Opportunities'),
              form_id='SaleOpportunityModule_viewSaleOpportunityStatusList'))

return result
