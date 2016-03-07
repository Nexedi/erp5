"""
This script notify the user that the form has been submitted
"""
from Products.DCWorkflow.DCWorkflow import ValidationFailed


translateString = context.Base_translateString
portal_catalog = context.portal_catalog

form = state_change['object']

# Build the message and translate it
msg = []
subject = translateString("Your application has been submitted successfully under the reference") + " : " + form.getId()
msg.append(subject)
msg.append(translateString("An Agent will review your application shortly. You will be notified by email whenever your application will start being processed. To further track your application, connect and login any time to the following site"))
msg.append(context.getWebSiteValue().getAbsoluteUrl())
msg.append(translateString("And use the login") + " : " + form.getReference())
msg.append(translateString("and the password") + " : " + form.getPassword())

msg = "\n".join(msg)

# We can now notify the accoutant through the notification tool
context.portal_notifications.sendMessage(recipient=form.getReference(), 
    subject=subject, message=msg, portal_type_list=('Subscription Form'),
    store_as_event=True)
