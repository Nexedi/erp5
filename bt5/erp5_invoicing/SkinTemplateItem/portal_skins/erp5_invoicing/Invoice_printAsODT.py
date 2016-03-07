if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 10)

return context.Invoice_viewAsODT(format=format)
