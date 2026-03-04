"""Project-app RSS deep-link for this post's thread (push_history_stored_state).

Provider for the erp5_discussion DiscussionPost_getRSSItemUrl seam. The RSS feed is
served front-side on the project-app.
"""
portal = context.getPortalObject()
base_url = portal.absolute_url()
thread = context.getParentValue()
forum = thread.DiscussionThread_getDiscussionForum()
if forum is None:
  return ''
return ('%s/#!push_history_stored_state?p.jio_key=%s&p.page=form&p.view=view&'
        'n.jio_key=%s&n.page=form&n.view=view&n.last_post=%s'
        % (base_url, forum.getRelativeUrl(), thread.getRelativeUrl(),
           thread.DiscussionThread_getDiscussionPostCount()))
