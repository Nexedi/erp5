from Products.ERP5Form.Report import ReportSection
request = container.REQUEST
return ReportSection(form_id='DeliveryModule_viewDeliveryLineList',
                     path=context.getPhysicalPath(),
                     selection_params=dict(portal_type=request['portal_type'],
                                           module_selection_name=request['selection_name'])),
