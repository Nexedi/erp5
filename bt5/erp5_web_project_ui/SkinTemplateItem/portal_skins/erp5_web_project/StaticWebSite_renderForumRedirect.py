"""
Forum-migration resolver: the render method of the `forum_redirect` Static Web
Section. Every migrated old-forum sub-path 301s here (sub-path appended to
redirect_domain), and this turns it into the right project-app destination, or
serves the RSS feed in place.

source_path shapes (segments after the forum_redirect section):
  discussion_forum_module/<id>                                  -> forum index
  discussion_forum_module/<id>/<thread-reference>[/view...]     -> a thread
  discussion_forum_module/<id>/WebSection_viewLatestDiscussionPostListAsRSS -> RSS feed
"""
REQUEST = context.REQUEST
portal = context.getPortalObject()

RSS_SCRIPT_ID = 'WebSection_viewLatestDiscussionPostListAsRSS'
VALID_STATE_TUPLE = ('published', 'published_alive', 'released', 'released_alive',
                     'shared', 'shared_alive')

base_url = context.Base_getProjectAppBaseUrl()
part_list = [x for x in (REQUEST.other.get('source_path') or '').split('/') if x]

# Expect discussion_forum_module/<id> as the first two segments
if len(part_list) < 2 or part_list[0] != 'discussion_forum_module':
  return context.Base_redirect(base_url, status_code=302)

forum = portal.restrictedTraverse('/'.join(part_list[:2]), None)
if forum is None:
  return context.Base_redirect(base_url, status_code=302)
remainder = part_list[2:]

# RSS feed: serve in place (the access token is already bound to this URL)
if remainder and remainder[0] == RSS_SCRIPT_ID:
  return forum.DiscussionForum_viewLatestPostListAsRSS()

# Forum index
if not remainder:
  return context.Base_redirect('%s/#/%s' % (base_url, forum.getRelativeUrl()),
                               status_code=302)

# A thread: resolve the reference, deep-link to its last post
thread_list = portal.portal_catalog(portal_type='Discussion Thread',
                                    reference=remainder[0],
                                    validation_state=VALID_STATE_TUPLE,
                                    limit=1)
if not thread_list:
  return context.Base_redirect('%s/#/%s' % (base_url, forum.getRelativeUrl()),
                               status_code=302)

thread = thread_list[0].getObject()
redirect_url = ('%s/#!push_history_stored_state?'
                'p.jio_key=%s&p.page=form&p.view=view&'
                'n.jio_key=%s&n.page=form&n.view=view&n.last_post=%s'
                % (base_url, forum.getRelativeUrl(), thread.getRelativeUrl(),
                   thread.DiscussionThread_getDiscussionPostCount()))
return context.Base_redirect(redirect_url, status_code=302)
