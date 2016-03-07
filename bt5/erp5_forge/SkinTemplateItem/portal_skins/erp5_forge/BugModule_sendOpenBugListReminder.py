portal = context.getPortalObject()
bug_module = portal.bug_module
server_url = portal.ERP5Site_getAbsoluteUrl()

body_text_line_list = []
addBodyLine = body_text_line_list.append
bug_count = 0

assigned_to_dict={}
not_assigned_bug_list=[]

for bug in bug_module.searchFolder(portal_type='Bug',
                                   simulation_state=('confirmed', 'set_ready',),
                                   sort_on=(('id', 'asc', 'int'),)):
  bug = bug.getObject()
  if bug.getSource():
    assigned_to_dict.setdefault(bug.getSource(), []).append(bug)
  else:
    not_assigned_bug_list.append(bug)
  bug_count += 1

for assignee, bug_list in assigned_to_dict.items():
  addBodyLine(" Assigned to %s:" % bug_list[0].getSourceTitle())
  for bug in bug_list:
    addBodyLine("  [%s] %s" % (bug.getReference(), bug.getTitle()))
    addBodyLine("    %s/%s/view" % (server_url, bug.getRelativeUrl()))
    addBodyLine('')
  addBodyLine('')

if not_assigned_bug_list:
  addBodyLine('')
  addBodyLine(" Not assigned:")
  for bug in not_assigned_bug_list:
    addBodyLine("  [%s] %s" % (bug.getReference(), bug.getTitle()))
    addBodyLine("    %s/%s/view" % (server_url, bug.getRelativeUrl()))
    addBodyLine('')

if bug_count:
  portal.portal_notifications.sendMessage(sender=None,
                          recipient=[],
                          subject="%s: %s Open Bugs" % (portal.title_or_id(), bug_count,),
                          message='\n'.join(body_text_line_list))
