"""Create a new credential update"""
portal_status_message=""
person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if person is None:
  portal_status_message = context.Base_translateString("Can't find corresponding person, it's not possible to update your credentials.")
else:
  organisation = person.getSubordinationValue()
  if organisation is None:
    portal_status_message = context.Base_translateString("Can't find corresponding organisation, it's not possible to update your credentials.")
  else:
    # create the credential update
    module = context.getDefaultModule(portal_type='Credential Update')
    credential_update = module.newContent(
        portal_type="Credential Update",
                    default_email_text=default_email_text,
                    default_telephone_text=default_telephone_text,
                    default_mobile_telephone_text=default_mobile_telephone_text,
                    default_fax_text=default_fax_text,
                    default_address_street_address=default_address_street_address,
                    default_address_city=default_address_city,
                    default_address_zip_code=default_address_zip_code,
                    default_address_region=default_address_region,
                    activity_list=activity_list,
                    destination_decision=organisation.getRelativeUrl(),
                    default_image_file=default_image_file,
                    description=description)

    credential_update.submit()
    portal_status_message = context.Base_translateString("Credential Update Created.")

return context.Base_redirect(dialog_id, keep_items = dict(portal_status_message=portal_status_message ))
