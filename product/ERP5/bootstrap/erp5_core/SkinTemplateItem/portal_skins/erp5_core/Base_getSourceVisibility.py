# controls the visibility of "developper mode" links in ERP5 web interface
# (edit form, edit field, edit portal type, ...) for object

if obj is None:
  obj = context

return context.portal_preferences.getPreferredHtmlStyleDevelopperMode() and context.portal_membership.checkPermission('View management screens', obj)
