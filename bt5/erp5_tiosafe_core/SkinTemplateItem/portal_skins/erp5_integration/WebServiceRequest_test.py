# Build parameter dict
parameter_list= parameters.split("\n")
parameter_dict = {}
for parameter in parameter_list:
  try:
    k,v = parameter.split('=')
  except ValueError:
    continue
  parameter_dict[k] = v


translateString = context.Base_translateString

object_list = context(test_mode=True, **parameter_dict)

result_list = []

if context.getLastRequestError() is None:
  error = None
  for obj in object_list:
    try:
      xml = obj.asXML(debug=True)
    except (ValueError, NotImplementedError) as msg:
      error = msg
      continue
    if not xml:
      error = "Check your mapping, some might be missing"
    else:
      result_list.append(xml,)


  if error:
    context.edit(last_request_error = "%r" %(error,))

context.edit(last_request_tiosafe_xml_result='\n'.join(result_list))

portal_status_message = translateString("Request Executed.")
context.Base_redirect("WebServiceRequest_viewTestResult", keep_items = dict(portal_status_message=portal_status_message))
