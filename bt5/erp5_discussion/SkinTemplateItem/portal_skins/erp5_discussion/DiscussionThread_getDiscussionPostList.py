"""
  This script gets list of Discussion Posts for a Discussion Thread
  using catalog.
  Due to asynchronous nature of catalog it can use
  passed from REQUEST not index yet posts.
"""
post_relative_url = context.REQUEST.get('post_relative_url')
discussion_post_list = [x.getObject() for x  in context.searchFolder(**kw)]

if post_relative_url is not None:
  post = context.restrictedTraverse(post_relative_url)
  if post is not None and post not in discussion_post_list:
    discussion_post_list.append(post)
return discussion_post_list
