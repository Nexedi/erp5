from Products.ERP5Type.Message import translateString

working_copy = repository
context.getVcsTool(path=working_copy).createBusinessTemplateWorkingCopy()

return context.Base_redirect('view', keep_items=dict(
  portal_status_message=translateString('Business Template Working Copy created')
))
