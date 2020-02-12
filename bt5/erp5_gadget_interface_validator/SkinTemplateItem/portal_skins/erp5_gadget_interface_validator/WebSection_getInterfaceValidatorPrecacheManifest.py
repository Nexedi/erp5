# Add all ERP5JS gadget
url_list = [
  'gadget_erp5_page_validator_report.html',
  'gadget_erp5_page_validator_report.js',
  'gadget_erp5_page_validator_result_list.html',
  'gadget_erp5_page_validator_result_list.js',
  'gadget_interface_validator_panel.html',
  'gadget_interface_validator_panel.js',
  'gadget_interface_validator_jio.html',
  'gadget_interface_validator_jio.js',
  'gadget_interface.html',
  'gadget_interface.js',
  'gadget_interface_loader.html',
  'gadget_interface_loader.js',
]

if REQUEST is not None:
  import json
  REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
  return json.dumps(dict.fromkeys(url_list), indent=2)

return url_list
