def cleanupDescription(requirement):
  description = requirement.getDescription('').replace('\r\n', '\n')
  new_description = ''
  for i, char in enumerate(description):
    if char == ' ':
      # strip double spaces
      if len(description) > i and description[i + 1] == ' ':
        continue
    # replace \n between words by spaces
    if char == '\n' and i > 1 and description[i - 1] != '.':
      new_description += ' '
      continue

    new_description += char

  requirement.edit(description=new_description)

  # continue recursively
  for sub_requirement in requirement.contentValues(
               checked_permission='Modify portal content'):
    cleanupDescription(sub_requirement)

cleanupDescription(context)

return context.Base_redirect(form_id,
  keep_items=dict(portal_status_message=
                     context.Base_translateString('Descriptions cleaned up.')))
