modification_date = context.getModificationDate()

# Ensure that if the web site policy is just set to Must-Revalidate, all documents are updated.
# It forces HTTP Cache middleware to refresh there contents.
is_web_mode = (context.REQUEST.get('current_web_section', None) is not None) or (hasattr(context, 'isWebMode') and context.isWebMode())
if is_web_mode:
  modification_date = max(modification_date, context.getWebSectionValue().getModificationDate())

return modification_date
