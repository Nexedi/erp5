"""Proxy Role Auditor is required to create activity
"""
portal = context.getPortalObject()
portal_type = 'Web Message'
module = portal.getDefaultModule(portal_type)

translate = portal.Base_translateString

edit_kw = {'portal_type': portal_type,
           'title': title,
           'start_date': DateTime(),
           'source_organisation_title': source_organisation_title,
           'source_person_first_name': source_person_first_name,
           'source_person_last_name': source_person_last_name,
           'source_person_default_email_text': source_person_default_email_text,
           'source_person_default_telephone_text': source_person_default_telephone_text,
           'text_content': text_content,
           'content_type': 'text/plain',
           'resource': resource,
           'source_carrier': context.getWebSectionValue().getRelativeUrl(),
          }
connected_user = portal.portal_membership.getAuthenticatedMember().getUserValue()
if connected_user is not None:
  edit_kw['source'] = connected_user.getRelativeUrl()

# We do not call portal_contribution for two reasons:
# 1- Metadata discovery will be run by alarms with allowed user to access other documents.
# 2- A proxy role can not wrap portal_contributions calls and disallow Anonymous user to create the document.
tag = 'incoming_web_message'
edit_kw['activate_kw'] = {'tag': tag}
module.activate(tag=tag, activity='SQLQueue').EventModule_addWebMessage(**edit_kw)

# Trigger explicitly the alarm which will run discoverMetadata on created event, then
# Fill in discoverable properties (sender, recipient, ...) and change workflow states.
# XXX hardcoded id, must be picked up by reference and version API
portal.portal_alarms.fetch_incoming_web_message_list.activate(after_tag=tag).activeSense()

portal_status_message = translate('Your message has been successfully submitted.')
context.getWebSectionValue().getParentValue().Base_redirect(keep_items={'portal_status_message': portal_status_message})
