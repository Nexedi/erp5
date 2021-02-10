if context.AccountingTransaction_isSourceView():
  section_list = [
      context.getSourceSectionValue(portal_type='Organisation'),
      context.getDestinationSectionValue(portal_type='Organisation'),
  ]
else:
  section_list = [
      context.getDestinationSectionValue(portal_type='Organisation'),
      context.getSourceSectionValue(portal_type='Organisation'),
  ]

for section in section_list:
  if section is not None:
    if section.getGroup():
      return section.getGroup()

return context.Base_getPreferredAttachedDocumentGroup()
