import base64
portal = context.getPortalObject()

# Update Photos
for record in portal.expense_record_module.objectValues(portal_type="Expense Record"):
  ticket = record.getFollowUpValue()
  photo_data = record.getPhotoData()
  if photo_data:
    if "," in photo_data and ticket:
      if ticket.getReference():
        photo_data = photo_data.split(",")[1]
        image = portal.portal_contributions.newContent(
          data = base64.b64decode(photo_data),
          reference=ticket.getReference()+ "-justificatif",
          title = ticket.getReference() + " Justificatif",
          description = ticket.getDescription(),
          filename="tmp.png",
          follow_up=ticket.getRelativeUrl(),
          publication_section=portal.ERP5Site_getPreferredExpenseDocumentPublicationSectionValue().getRelativeUrl(),
        )
        image.share()
      else:
        print(ticket.getRelativeUrl())

print(DateTime())
#return printed


for i in context.portal_catalog(portal_type='Expense Validation Request'):
  sourceReference = i.getSourceReference()
  if sourceReference:
    if i.getReference() != sourceReference:
      if migrate:
        i.setReference(sourceReference)
      print(i.getRelativeUrl())

return printed
