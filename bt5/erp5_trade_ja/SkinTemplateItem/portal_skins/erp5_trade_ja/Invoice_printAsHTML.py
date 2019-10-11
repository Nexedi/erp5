if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 10)

container.REQUEST.set('format', 'pdf')
return context.getPortalObject().web_page_module.newContent(
  portal_type='Web Page',
  temp_object=True,
  title=context.getReference(),
  text_content=context.Invoice_viewAsHTML()).index_html(container.REQUEST)
