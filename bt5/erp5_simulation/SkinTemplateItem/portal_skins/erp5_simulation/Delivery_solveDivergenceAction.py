"""
if context.Delivery_getSolverProcess() is None:
  message = context.Base_translateString("Workflow state may have been updated by other user. Please try again.")
  return context.Base_redirect('view',
                                keep_items={'portal_status_message': message})
"""
return context.Base_renderForm('Delivery_viewSolveDivergenceDialog')
