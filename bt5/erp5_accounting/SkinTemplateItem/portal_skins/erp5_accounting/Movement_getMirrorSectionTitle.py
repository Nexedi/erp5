"""Retrieve the title of the mirror section
"""
if brain.mirror_section_uid:
  movement = brain.getObject()
  if brain.mirror_section_uid == movement.getDestinationSectionUid():
    return movement.getDestinationSectionTitle()
  return movement.getSourceSectionTitle()
