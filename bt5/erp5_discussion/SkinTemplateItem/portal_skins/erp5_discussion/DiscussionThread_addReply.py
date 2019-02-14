assert context.getPortalType() == "Discussion Thread"

title = "Re: " + context.getTitle()

context.DiscussionThread_createPost(title, text_content)

portal_status_message = "New post created"
context.Base_redirect("view", keep_items = dict(portal_status_message = portal_status_message))
