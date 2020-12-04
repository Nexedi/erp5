from Products.ERP5Type.Message import translateString

form_results = context.BusinessTemplate_viewCreateWorkingCopy.validate_all(REQUEST)
working_copy = form_results['your_repository']
context.getVcsTool(path=working_copy).createBusinessTemplateWorkingCopy()

return context.Base_redirect('BusinessTemplate_viewVcsStatus', keep_items=dict(
  portal_status_message=translateString('Business Template Working Copy created')
))
