if context.getValidationState() == 'posted':
  return context.Base_redirect('view_traceability_data')
delivery = context.getCausalityValue(portal_type='Manufacturing Execution')
return delivery.Base_redirect('view_traceability_input')
