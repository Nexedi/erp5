"""
This script tries to send a message containing the credentials to the
organisation. It uses portal_notifications and the getObject API of ERP5Catalog.
"""
from Products.DCWorkflow.DCWorkflow import ValidationFailed


translateString = context.Base_translateString
portal_catalog = context.portal_catalog
vat_code = context.getVatCode()

# get the new organisation :
result = portal_catalog(portal_type='Organisation',
    vat_code=vat_code)

if len(result) > 1:
  msg = "Error : There is more than one company with the NINEA code ${code}"
  msg = translateString(msg, mapping=dict(code=vat_code))
  raise ValidationFailed(msg) 

if len(result) == 0:
  msg = "No organisation with the NINEA code ${code}"
  msg = translateString(msg, mapping=dict(code=vat_code))
  raise ValidationFailed(msg) 

organisation = result[0]

# Build the message and translate it
subject = translateString("Your credential for ${site_address}", mapping=dict(site_address='www.erp5.org'))
msg = """Thanks for registrering to ERP5. Now you can connect in on ${site_address} with this credentials : 

Login : ${login}
Password : ${password}

This credentials are usefull to track your application and more. Please visit ${site_address} for more information.
"""
msg = translateString(msg,
             mapping=dict(site_address='www.erp5.org',
                          login=organisation.getReference(),
                          password=organisation.getPassword())
            )

# We can now notify the owner through the notification tool
context.portal_notifications.sendMessage(recipient=organisation.getReference(), 
    subject=subject, message=msg, portal_type_list=('Person', 'Organisation'),
    store_as_event=True)
