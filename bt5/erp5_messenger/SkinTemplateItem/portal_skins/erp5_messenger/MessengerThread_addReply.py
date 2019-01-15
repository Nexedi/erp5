assert context.getPortalType() == "Messenger Thread"

portal = context.getPortalObject()

person = context.ERP5Site_getAuthenticatedMemberPersonValue()
person = portal.person_module.get("roqueporchetto")
#TODO get person from user/autenticatedMember

title = "Re: " + context.getTitle()

messenger_post = portal.messenger_post_module.newContent(
                    title = title,
                    text_content = text_content,
                    source_value = person,
                    follow_up_value = context,
                    portal_type = "Messenger Post"
)

portal_status_message = "New post created"
context.Base_redirect("view", keep_items = dict(portal_status_message = portal_status_message))
