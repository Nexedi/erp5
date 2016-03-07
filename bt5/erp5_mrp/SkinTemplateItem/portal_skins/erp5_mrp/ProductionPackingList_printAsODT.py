if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 10)

return context.ProductionPackingList_viewAsODT(format=format)
