"""Return the 'side-specific' reference, ie. the source reference or
destination reference.
"""
delivery = brain.getObject().getExplanationValue()
if brain.section_uid != brain.mirror_section_uid:
  if delivery.getSourceSectionUid() == brain.section_uid:
    return delivery.getSourceReference()
  return delivery.getDestinationReference()

# If we have a movement which exists for both section uid and mirror section uid,
# we can only guess what reference should be used.
if round(brain.total_quantity - brain.getObject().getQuantity(), 5) == 0:
  return delivery.getDestinationReference()

return delivery.getSourceReference()
