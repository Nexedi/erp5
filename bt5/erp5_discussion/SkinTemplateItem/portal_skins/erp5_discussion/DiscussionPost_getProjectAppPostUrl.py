"""Project-app RSS deep-link for this post's thread, or '' when the project app
(erp5_project / Base_getProjectAppBaseUrl) is not installed - so erp5_discussion
does not hard-depend on erp5_project.
Only caller: DiscussionForum_viewLatestPostListAsRSS/listbox_link (the project-app forum RSS feed served from the forum object); unrelated to the Static Web Section redirect."""
get_base = getattr(context, 'Base_getProjectAppBaseUrl', None)
if get_base is None:
  return ''
thread = context.getParentValue()
forum = thread.DiscussionThread_getDiscussionForum()
if forum is None:
  return ''
return ('%s/#!push_history_stored_state?p.jio_key=%s&p.page=form&p.view=view&'
        'n.jio_key=%s&n.page=form&n.view=view&n.last_post=%s'
        % (get_base(), forum.getRelativeUrl(), thread.getRelativeUrl(),
           thread.DiscussionThread_getDiscussionPostCount()))
