if context.REQUEST.has_key('workflow_action'): # We are on a workflow transition
  help = '%s#%s' % (getattr(getattr(context, form_id), 'form_action'),context.REQUEST['workflow_action'])
elif action is not None:
  help = '%s#%s' % (context.getPortalTypeName(), action)
elif form_id is not None:
  help = '%s_%s' % (context.getPortalTypeName(), form_id)
else:
  help = context.getPortalTypeName()
return '%s/%s' % (context.portal_preferences.getPreferredHtmlStyleDocumentationBaseUrl(), help)
