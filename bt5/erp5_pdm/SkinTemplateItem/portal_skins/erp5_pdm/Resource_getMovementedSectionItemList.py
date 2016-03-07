"""Returns an item list of all mirror sections that have been used in movements with this resource.
"""

item_list = [('', '')]
portal = context.getPortalObject()
getobject = portal.portal_catalog.getobject

for x in portal.portal_simulation.getInventoryList(
                              resource_uid=context.getUid(),
                              group_by_mirror_section=1):
  mirror_section_uid = x.mirror_section_uid
  if mirror_section_uid:
    mirror_section = getobject(mirror_section_uid)
    item_list.append((mirror_section.getTitle(),
                      mirror_section.getRelativeUrl()))

item_list.sort(key=lambda x:x[0])
return item_list
