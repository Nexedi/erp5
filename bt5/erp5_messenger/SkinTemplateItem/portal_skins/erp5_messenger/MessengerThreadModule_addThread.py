portal = context.getPortalObject()

person = context.ERP5Site_getAuthenticatedMemberPersonValue()
person = portal.person_module.get("roqueporchetto")
#TODO get person from user/autenticatedMember

messenger_thread = portal.messenger_thread_module.newContent(
                    title = thread_title,
                    portal_type = "Messenger Thread"
)

messenger_thread.setReference(messenger_thread.getId())

messenger_post = portal.messenger_post_module.newContent(
                    title = thread_title,
                    text_content = text_content,
                    source_value = person,
                    follow_up_value = messenger_thread,
                    portal_type = "Messenger Post"
)

portal_status_message = "New thread created"
context.Base_redirect("view", keep_items = dict(portal_status_message = portal_status_message))
