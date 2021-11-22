# this API uses format=
# pylint:disable=redefined-builtin
if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 150)

return context.PackingList_viewAsODT(format=format)
