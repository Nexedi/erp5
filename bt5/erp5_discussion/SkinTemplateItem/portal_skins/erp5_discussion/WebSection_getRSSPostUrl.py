web_section = context.REQUEST.get('current_web_section')
thread = post.getParentValue()
is_migrated = (web_section is not None and
               web_section.getCustomRenderMethodId() == 'WebSection_redirectToProjectForum')

if is_migrated:
  return '%s/#/%s?page=form&view=view&last_post=%s' % (
    context.Base_getProjectAppBaseUrl(),
    thread.getRelativeUrl(),
    thread.DiscussionThread_getDiscussionPostCount()
  )

# Fallback: standard web section URL for non-migrated forums
return '%s/%s/view?list_start=%s&reset=1#%s' % (
  context.REQUEST['URL1'],
  thread.getReference(),
  post.getId(),
  post.getUid()
)
