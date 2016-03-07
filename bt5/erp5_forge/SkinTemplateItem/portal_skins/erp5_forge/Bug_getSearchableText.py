full_text = []
for message in context.contentValues(portal_type='Bug Line'):
  full_text.append(message.getTextContent(""))
return ' '.join([x for x in full_text if x])
