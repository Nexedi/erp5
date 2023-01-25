portal = context.getPortalObject()
preferred_forum_quote_original_message= portal.ERP5Site_getUserPreferredForumSettingsDict()['preferred_forum_quote_original_message']

if discussion_post_uid is not None:
  # set title & text_content
  discussion_post = getattr(context, discussion_post_uid)

  title = discussion_post.getTitle()
  if not title.lower().startswith('re:'):
    # stop exploding "Re: Re: .." to one level
    title = 'Re: %s' %title
  context.REQUEST.set('discussion_post_title', title)
  if preferred_forum_quote_original_message:
    author_dict = discussion_post.DiscussionPost_getAuthorDict()
    text_content = '<blockquote>From: %s<br/>%s</blockquote><br/>' %(author_dict['author_title'],
                                                               discussion_post.getTextContent())
    context.REQUEST.set('discussion_post_text_content', text_content)

return context.DiscussionThread_viewCreateNewDiscussionPostDialog()
