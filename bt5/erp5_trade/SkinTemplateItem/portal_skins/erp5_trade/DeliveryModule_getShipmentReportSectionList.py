from builtins import str
from Products.ERP5Form.Report import ReportSection
from Products.ERP5Type.Message import translateString
request = container.REQUEST

report_section_list = []
if request['delivery_line_list_mode']:
  report_section_list.append(
    ReportSection(
        form_id='DeliveryModule_viewShipmentLineList',
        path=context.getPhysicalPath(),
        title=str(translateString(context.DeliveryModule_viewShipmentLineList.getProperty('title'))),
        selection_params=dict(module_selection_name=request['selection_name'])))
if request['delivery_list_mode']:
  report_section_list.append(
    ReportSection(
        form_id='DeliveryModule_viewShipmentDeliveryList',
        path=context.getPhysicalPath(),
        title=str(translateString(context.DeliveryModule_viewShipmentDeliveryList.getProperty('title'))),
        selection_params=dict(module_selection_name=request['selection_name'])))

return report_section_list
