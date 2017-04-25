item_list = [('', '')]
portal = context.getPortalObject()
getobject = portal.portal_catalog.getobject

for x in portal.portal_simulation.getInventoryList(
                              portal_type=('Pay Sheet Cell',
                                           'Pay Sheet Line'),
                              only_accountable=False,
                              group_by_resource=0,
                              group_by_section=0,
                              group_by_mirror_section=1):
  mirror_section_uid = x.mirror_section_uid
  if mirror_section_uid:
    mirror_section = getobject(mirror_section_uid)
    if mirror_section.getPortalType() == 'Organisation':
      item_list.append((mirror_section.getTitle(),
                        mirror_section.getRelativeUrl()))

item_list.sort(key=lambda a:a[0])
return item_list
