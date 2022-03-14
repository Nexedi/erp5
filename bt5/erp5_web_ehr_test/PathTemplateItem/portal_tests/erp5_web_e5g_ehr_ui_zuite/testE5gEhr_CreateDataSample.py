from builtins import str
from builtins import range
portal =  context.getPortalObject()

"""Delete objects we are about to create """
for i in range(start, start + num):
  if getattr(portal.position_announcement_module, 'announcement_' + str(i), None) is not None:
    portal.position_announcement_module.deleteContent('announcement_' + str(i))
  if getattr(portal.position_opportunity_module, 'opportunity_' + str(i), None) is not None:
    portal.position_opportunity_module.deleteContent('opportunity_' + str(i))
  if getattr(portal.position_module, 'position_' + str(i), None) is not None:
    portal.position_module.deleteContent('position_' + str(i))

"""Create objects with given parameters"""
for i in range(start, start + num):
  portal.position_announcement_module.newContent(id = 'announcement_' + str(i), title = 'Super Announcement Title %d' % i, portal_type='Position Announcement')
  portal.position_opportunity_module.newContent(id = 'opportunity_' + str(i), title = 'Super Opportunity %d' % i, portal_type='Position Opportunity')
  portal.position_module.newContent(id = 'position_' + str(i), title = 'Super Position %d' % i, portal_type='Position')

return 'Created Successfully.'
