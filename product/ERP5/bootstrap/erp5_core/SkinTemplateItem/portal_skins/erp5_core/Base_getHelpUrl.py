if context.REQUEST.has_key('workflow_action'): # We are on a workflow transition
  help_relative_url = '%s#%s' % (getattr(getattr(context, form_id), 'form_action'),context.REQUEST['workflow_action'])
elif action is not None:
  help_relative_url = '%s#%s' % (context.getPortalTypeName(), action)
elif form_id is not None:
  help_relative_url = '%s_%s' % (context.getPortalTypeName(), form_id)
else:
  help_relative_url = context.getPortalTypeName()
return '%s/%s' % (context.portal_preferences.getPreferredHtmlStyleDocumentationBaseUrl(), help_relative_url)
