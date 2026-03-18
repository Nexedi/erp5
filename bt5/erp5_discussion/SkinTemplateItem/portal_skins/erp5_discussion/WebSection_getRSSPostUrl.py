thread = post.getParentValue()
is_migrated = (context.getCustomRenderMethodId() == 'WebSection_redirectToProjectForum')

if is_migrated:
  return '%s/#/%s?page=form&view=view&last_post=%s' % (
    context.Base_getProjectAppBaseUrl(),
    thread.getRelativeUrl(),
    thread.DiscussionThread_getDiscussionPostCount()
  )

return '%s/%s/view?list_start=%s&reset=1#%s' % (
  context.REQUEST['URL1'],
  thread.getReference(),
  post.getId(),
  post.getUid()
)
