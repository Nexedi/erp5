# pylint:disable=redefined-builtin
if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 10)

return context.PaySheetTransaction_viewAsODT(format=format)
