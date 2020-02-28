# Add all ERP5JS gadget
url_list = [
  'gadget_interface_validator_test_correct_implemented_gadget.html',
  'gadget_interface_validator_test_correct_implemented_gadget.js',
  'gadget_interface_validator_test_nonexistent_gadget.html',
  'gadget_interface_validator_test_nonexistent_gadget.js',
  'gadget_interface_validator_test_invalid_interface_gadget.html',
  'gadget_interface_validator_test_invalid_interface_gadget.js',
  'gadget_interface_validator_test_missing_interface_declaration_gadget.html',
  'gadget_interface_validator_test_missing_interface_declaration_gadget.js',
  'gadget_interface_validator_test_missing_method_declaration_gadget.html',
  'gadget_interface_validator_test_missing_method_declaration_gadget.js',
  'gadget_interface_validator_test_multiple_interface_correct_implemented_gadget.html',
  'gadget_interface_validator_test_multiple_interface_correct_implemented_gadget.js',
  'gadget_interface_validator_test_multiple_interface_duplicated_method_name.html',
  'gadget_interface_validator_test_multiple_interface_duplicated_method_name.js',
  'gadget_interface_validator_test_unknown_method_declaration_gadget.html',
  'gadget_interface_validator_test_unknown_method_declaration_gadget.js',
]

if REQUEST is not None:
  import json
  REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
  return json.dumps(dict.fromkeys(url_list), indent=2)

return url_list
