help = context.getPortalTypeName()
if workflow_action is not None: # First, the workflow transition case.
  help = '%s_%s' % (help, workflow_action)
elif current_action is not None: # Then, we are able to get the action.
  help = '%s_%s' % (help, current_action['id'])
elif current_form_id is not None: # Otherwise, get the form we are in.
  help = '%s_%s' % (help, current_form_id)
return '%s/%s' % (context.portal_preferences.getPreferredHtmlStyleDocumentationBaseUrl(), help)
