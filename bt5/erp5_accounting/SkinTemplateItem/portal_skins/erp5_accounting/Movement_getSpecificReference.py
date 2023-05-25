"""Return the 'side-specific' reference, ie. the source reference or
destination reference.
"""
delivery = brain.getObject().getExplanationValue()
is_source = brain.is_source

if is_source is None:
  # BBB on old data, is_source is NULL
  if brain.section_uid != brain.mirror_section_uid:
    is_source = delivery.getSourceSectionUid() == brain.section_uid
  # If we have a movement which exists for both section uid and mirror section uid,
  # we can only guess what reference should be used.
  is_source = round(brain.total_quantity - brain.getObject().getQuantity(), 5) != 0


return delivery.getSourceReference() if is_source else delivery.getDestinationReference()
