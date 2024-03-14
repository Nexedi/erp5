if context.REQUEST.REQUEST_METHOD != "POST":
  return "pong"

text_content = context.REQUEST.get('BODY')
context.log(text_content)
connector = context.ERP5Site_getCxmlConnectorValue()
shared_secret_text = "<SharedSecret>%s</SharedSecret>" %connector.getPassword()
if shared_secret_text not in text_content.replace(' ', ''):
  return connector.CxmlConnector_getResponse(
    code=200,
    text="Unauthorized",
    content="Error:Invalid or unrecognized sender credentials")

if "<ProfileRequest>" in text_content:
  return connector.CxmlConnector_getProfileResponse()

cxml_document = context.cxml_document_module.newContent(
  portal_type="Cxml Document",
  text_content=text_content)
cxml_document.activate().process()
return connector.CxmlConnector_getResponse()
