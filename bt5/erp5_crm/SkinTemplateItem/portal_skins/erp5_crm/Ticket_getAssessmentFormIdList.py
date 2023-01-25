"""
This script returns the list of forms that will be used as assessment forms on events
"""

from Products.ERP5Type.Cache import CachingMethod

def getFormItemList():
  result = [('', '')]
  form_id_list = context.portal_preferences.getPreferredEventAssessmentFormIdList()
  for form_id in form_id_list:
    form = getattr(context.getPortalObject(), form_id, None)
    if form is not None:
      result.append((context.Localizer.erp5_ui.gettext(form.title) or form_id, form_id))
  return result

getFormItemList = CachingMethod(getFormItemList,
      id=('Ticket_getFormItemList', context.Localizer.get_selected_language()),
      cache_factory='erp5_ui_long')

return getFormItemList()
