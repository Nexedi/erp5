from Products.ERP5Type.Message import translateString

simulation_state = context.getSimulationState()

if simulation_state == 'processing':
  return context.Base_redirect(keep_items={'portal_status_message': translateString('AI Assistant is already processing')})

context.start()
return context.Base_redirect(keep_items={'portal_status_message': translateString('AI Assistant is requested')})
