if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 10)

context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf;')
context.REQUEST.RESPONSE.setHeader('Content-Disposition', 'filename="%s.pdf"' % context.getReference())

# [0] => mime
return context.getPortalObject().web_page_module.newContent(
  portal_type='Web Page',
  temp_object=True,
  text_content=context.Invoice_viewAsHTML()).convert('pdf')[1]
