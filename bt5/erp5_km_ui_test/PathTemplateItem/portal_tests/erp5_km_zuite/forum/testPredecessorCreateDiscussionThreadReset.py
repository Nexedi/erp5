"""
  Make sure the objects about to be created do not exist already
"""

portal = context.getPortalObject()

for x in portal.discussion_thread_module.objectValues():
  if x.getTitle() == "Thread 1":
    portal.discussion_thread_module.deleteContent(x.getId())
  if x.getTitle() == "Thread 2":
    portal.discussion_thread_module.deleteContent(x.getId())
  if x.getTitle() == "Thread 3":
    portal.discussion_thread_module.deleteContent(x.getId())

return 'Reset Successfully.'
