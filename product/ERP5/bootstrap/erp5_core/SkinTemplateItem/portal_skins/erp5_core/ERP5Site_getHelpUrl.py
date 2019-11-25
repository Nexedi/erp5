help_topic = context.getPortalTypeName()
if workflow_action is not None: # First, the workflow transition case.
  help_topic = '%s_%s' % (help_topic, workflow_action)
elif current_action is not None: # Then, we are able to get the action.
  help_topic = '%s_%s' % (help_topic, current_action['id'])
elif current_form_id is not None: # Otherwise, get the form we are in.
  help_topic = '%s_%s' % (help_topic, current_form_id)
return '%s/%s' % (context.portal_preferences.getPreferredHtmlStyleDocumentationBaseUrl(), help_topic)
