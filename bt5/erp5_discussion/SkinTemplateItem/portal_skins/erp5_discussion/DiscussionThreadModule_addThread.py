discussion_thread = context.getPortalObject().discussion_thread_module.newContent(
                    title = thread_title,
                    portal_type = "Discussion Thread"
)
discussion_thread.setReference(discussion_thread.getId())

discussion_thread.DiscussionThread_createPost(thread_title, text_content)

portal_status_message = "New thread created"
discussion_thread.Base_redirect("view", keep_items = dict(portal_status_message = portal_status_message))
