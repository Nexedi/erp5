use_ods_style = 1
if getattr(context.portal_skins, 'erp5_ods_style', None) is None:
  use_ods_style = 0

request = container.REQUEST
if use_ods_style:
  context.getPortalObject().portal_skins.changeSkin('ODS')
  request.set('portal_skin', 'ODS') # Some TALES expressions checks this
  request.set('reset', 1) # Some TALES expressions checks this

if target_language:
  request['AcceptLanguage'].set(target_language, 150)

form_report = getattr(context, print_mode)
return form_report(**kw)
