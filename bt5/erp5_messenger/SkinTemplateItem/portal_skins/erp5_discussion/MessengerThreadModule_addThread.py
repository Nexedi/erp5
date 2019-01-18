messenger_thread = context.getPortalObject().messenger_thread_module.newContent(
                    title = thread_title,
                    portal_type = "Messenger Thread"
)
messenger_thread.setReference(messenger_thread.getId())

messenger_thread.MessengerThread_createPost(thread_title, text_content)

portal_status_message = "New thread created"
messenger_thread.Base_redirect("view", keep_items = dict(portal_status_message = portal_status_message))
