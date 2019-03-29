"""
This script tries to send a message containing the credentials to the
person. It uses portal_notifications and the getObject API of ERP5Catalog.
"""
from Products.DCWorkflow.DCWorkflow import ValidationFailed


translateString = context.Base_translateString
portal_catalog = context.portal_catalog

# get the new person :
result = portal_catalog(portal_type='Person',
    title=context.getTitle(),
    default_email_text=context.getDefaultEmailText())

if len(result) > 1:
  msg = "Error : There is more than one person with the title ${title} and the email ${email}"
  msg = translateString(msg,
      mapping=dict(title=context.getTitle(),
        email=context.getDefaultEmailText()))
  raise ValidationFailed(msg)

if len(result) == 0:
  msg = "Error : No person with the title ${title} and the email ${email}"
  msg = translateString(msg,
      mapping=dict(title=context.getTitle(),
        email=context.getDefaultEmailText()))
  raise ValidationFailed(msg)

person = result[0]

# Build the message and translate it
subject = translateString("Your credential for ${site_address}", mapping=dict(site_address='www.erp5.org'))
msg = """Thanks for registrering to ERP5 EGov. Now you can connect in on ${site_address} with this credentials : 

Login : ${login}
Password : ${password}

This credentials are usefull to track your application and more. Please visit ${site_address} for more information.
"""
msg = translateString(msg,
             mapping=dict(site_address='www.erp5.org',
                          login=person.getReference(),
                          password=not_encrypt_password)
            )

# We can now notify the owner through the notification tool
context.portal_notifications.sendMessage(recipient=person.getReference(), 
    subject=subject, message=msg, portal_type_list=('Person', 'Organisation'),
    store_as_event=True)
