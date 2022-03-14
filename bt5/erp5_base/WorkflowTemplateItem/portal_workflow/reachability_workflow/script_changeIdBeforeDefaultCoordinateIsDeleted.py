coordinate = state_change['object']
if (coordinate.getId(), coordinate.getPortalType()) in (
  ('default_address', 'Address'),
  ('default_telephone', 'Telephone'),
  ('mobile_telephone', 'Telephone'),
  ('default_fax', 'Fax'),
  ('default_email', 'Email'),
  ('alternate_email', 'Email'),
):
  # In case of a document that has specific id used in content
  # accessors on parent, such as parent.getDefaultEmailValidationState(),
  # we cannot just delete the document, because it would break accessors
  # for security reasons.
  # To prevent this problem, we change the id on this document before
  coordinate.setId(
    coordinate.getParentValue().generateNewId()
  )
