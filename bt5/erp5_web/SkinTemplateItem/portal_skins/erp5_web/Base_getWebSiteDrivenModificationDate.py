modification_date = context.getModificationDate()

# Calculate the site root to prevent unexpected browsing
is_web_mode = (context.REQUEST.get('current_web_section', None) is not None) or (hasattr(context, 'isWebMode') and context.isWebMode())
# is_web_mode =  traversed_document.isWebMode()
if is_web_mode:
  modification_date = max(modification_date, context.getWebSectionValue().getModificationDate())

return modification_date
