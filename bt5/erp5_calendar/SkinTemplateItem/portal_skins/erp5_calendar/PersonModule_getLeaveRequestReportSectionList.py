from Products.ERP5Form.Report import ReportSection
request = container.REQUEST
return [ReportSection(path=context.getPhysicalPath(),
                      form_id='PersonModule_viewLeaveRequestReportSection',
                      selection_params=dict(from_date=request['from_date'],
                                            to_date=request['to_date'],
                                            node_category=request['node_category']))]
