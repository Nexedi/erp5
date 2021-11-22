if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 150)

return context.PaySheetTransaction_viewAsODT(format=format)
