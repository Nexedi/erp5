if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 10)

return context.ProductionOrder_viewAsODT(format=format)
