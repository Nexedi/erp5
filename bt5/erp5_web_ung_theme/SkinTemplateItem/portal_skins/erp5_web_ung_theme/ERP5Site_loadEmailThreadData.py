from json import dumps

portal = context.getPortalObject()
form = context.REQUEST.form

data_dict = {}

email_thread_uid = form.get("email_thread_uid")

email = portal.portal_catalog.getResultValue(portal_type="Email Thread",
                                             uid=email_thread_uid)

data_dict["subject"] = email.getTitle()
data_dict["to"] = email.getRecipient()
data_dict["cc"] = email.getCcRecipient()
data_dict["bcc"] = email.getBccRecipient()
data_dict["text_content"] = email.getTextContent()
data_dict["state"] = email.getValidationState()
data_dict["id"] = email.getId()

return dumps(data_dict)
