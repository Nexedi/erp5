if context.getValidationState() == 'new':
  context.portal_workflow.doActionFor(
      context,
      'read_action',
  )
