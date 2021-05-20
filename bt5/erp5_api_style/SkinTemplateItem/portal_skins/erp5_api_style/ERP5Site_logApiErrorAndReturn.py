import json
context.log(error_message)
if not text_content:
  text_content = context.REQUEST.get("BODY")
error = context.getPortalObject().error_record_module.newContent(
  portal_type="Error Record",
  description=str(error_message),
  text_content=str(text_content)
)
container.REQUEST.RESPONSE.setStatus(400)
# We follow here Paypal api guideline
# https://github.com/paypal/api-standards/blob/master/api-style-guide.md#error-schema
error_dict = {
  "debug_id": error.getId(),
  "status": error_code,
  "message": error_message
}
if error_name:
  error_dict["name"] = error_name
  error.setTitle(error_name)
if error_link:
  error_dict["link"] = error_link
if detail_list:
  error_dict["details"] = detail_list
  error.setDescription(str(error_message) + "\n".join([str(x) for x in detail_list]))
return json.dumps(error_dict, indent=2)
