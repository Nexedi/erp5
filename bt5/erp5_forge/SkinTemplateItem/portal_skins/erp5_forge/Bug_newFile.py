"""
  This script creates a new event with given metadata and
  attaches it to the current ticket.
"""
# pylint:disable=redefined-builtin
# this script uses file= argument

translateString = context.Base_translateString

default_bug_line = getattr(context, "default_bug_line", None)
if default_bug_line is None and context.getPortalType() == 'Bug':
  default_bug_line = context.newContent(id="default_bug_line",
                                        portal_type="Bug Line",
                                        title="Default Bug Line")
elif default_bug_line is None:
  default_bug_line = context

# Create a new File or Image Document
document = default_bug_line.newContent(portal_type=portal_type,
                                       description=description,
                                       title=title,
                                       file=file,
                                       reference=kw.get('reference'),
                                       version=kw.get('version'),
                                       language=kw.get('language'))

if context.getPortalType() == 'Bug':
  bug = context
else:
  bug = context.getParentValue()
body = """
New %s was added.
 Title: %s
 Description: %s
 Link: %s/view

 Bug Title: %s
 Bug Link: %s/view
""" % (document.getPortalType(),
       document.getTitle(), document.getDescription(),
       document.getAbsoluteUrl(), bug.getTitle(),
       bug.getAbsoluteUrl())

recipient_list= bug.Bug_getRecipientValueList()
sender = bug.Bug_getNotificationSenderValue()

portal = bug.getPortalObject()
portal.portal_notifications.sendMessage(sender=sender,
                          recipient=recipient_list,
                          subject="[ERP5 Bug] [New File] %s" % (bug.getTitle()),
                          message=body)

# Redirect to even
portal_status_message = translateString("New ${portal_type} added.",
                                    mapping = dict(portal_type = translateString(portal_type)))
return document.Base_redirect('view', keep_items = dict(portal_status_message=portal_status_message), **kw)
