from DateTime import DateTime

form = context.REQUEST.form

person = context.ERP5Site_getAuthenticatedMemberPersonValue()
sender_email = "freecloudalliance@freecloudalliance.org"

if person and person.getEmail():
  sender_email = person.getEmailText()

email_thread_module = context.email_thread_module
event_id = form.get("event_id")
if event_id:
  email = context.portal_catalog.getResultValue(portal_type="Email Thread", id=event_id)
else:
  email = email_thread_module.newContent(portal_type="Email Thread")

email.setStartDate(DateTime())
email.setSender(sender_email)
email.setRecipient(form.get("to"))
email.setCcRecipient(form.get("cc"))
email.setBccRecipient(form.get("bcc"))
email.setTitle(form.get("subject"))
email.setTextContent(form.get("text-content"))
if form.get("action") == "send-mail":
  context.portal_workflow.doActionFor(email, 'post_action')

return email.getId()
