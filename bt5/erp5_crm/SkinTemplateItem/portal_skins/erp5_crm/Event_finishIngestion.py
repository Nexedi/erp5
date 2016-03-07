"""
  This script is invoked at the end of ingestion process.
  The default behaviour is to receive messages so that they
  are marked as 'New' and appear in the worklist.
"""
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
portal_workflow = portal.portal_workflow

# Forwarded mail
forwarded_mail = False
subject = context.getContentInformation().get('Subject')
forwarded_mark_list = ('Fwd', 'Fw', 'Tr',)
if subject is not None and ':' in subject:
  if subject[0]=='[':# some email client enclose subject with '[]'
    subject = subject[1:]
  for mark in forwarded_mark_list:
    if subject.startswith(mark+':'):
      forwarded_mail = True
      break

if forwarded_mail is True:
  # find original recipient
  source = context.getSource()
  if source is not None:
    context.setDestination(source)

  # find original sender
  body = context.getTextContent()
  from_header = 'From: '
  from_header_length = len(from_header)
  Base_getEntityListFromFromHeader = context.Base_getEntityListFromFromHeader
  line = ''
  entity_list = []
  for line in body.split('\n'):
    if line.startswith(from_header):
      break
  if line:
    from_text = line[from_header_length:]
    entity_list.extend(Base_getEntityListFromFromHeader(from_text))
  if not entity_list:
    #Get data from attachments
    for attachment in context.getAttachmentInformationList():
      if 'From' in attachment:
        entity_list.extend(Base_getEntityListFromFromHeader(attachment['From']))
        break
  if entity_list:
    source = entity_list[0].getRelativeUrl()
    context.setSource(source)

if context.getPortalType() == 'Web Message' and\
   context.getSourceCarrierValue() is not None and\
   context.getSourceCarrierValue().getPortalType() in ('Web Message', 'Web Section',):
  # Read information about user and create person and/or related Organisation if any
  email_text = context.getSourcePersonDefaultEmailText()
  if email_text:
    person_portal_type = 'Person'
    organisation_portal_type = 'Organisation'
    person = None
    organisation = None
    if context.getSourcePersonFirstName() or context.getSourcePersonLastName():
      for validation_state in ('validated', '!= deleted'):
        person_email = portal.portal_catalog.getResultValue(
                          url_string={'query': email_text, 'key':'ExactMatch'},
                          portal_type='Email',
                          parent_portal_type=person_portal_type,
                          validation_state=validation_state,
                          parent_title='%s %s' % (context.getSourcePersonFirstName(''),
                                                  context.getSourcePersonLastName('')))
        if person_email is not None:
          person = person_email.getParentValue()
          break
    if context.getSourceOrganisationTitle():
      for validation_state in ('validated', '!= deleted'):
        organisation_email = portal.portal_catalog.getResultValue(
                          url_string={'query': email_text, 'key':'ExactMatch'},
                          portal_type='Email',
                          parent_portal_type=organisation_portal_type,
                          validation_state=validation_state,
                          parent_title=context.getSourceOrganisationTitle(''))
        if organisation_email is not None:
          organisation = organisation_email.getParentValue()
          break

    # XXX do we really want to create a person so easily ? Isn't it better to just setSourceFreeText on the event ?
    if person is None and (context.getSourcePersonFirstName() or context.getSourcePersonLastName()):
      person_module = portal.getDefaultModule(person_portal_type)
      person = person_module.newContent(portal_type=person_portal_type,
                                        first_name=context.getSourcePersonFirstName(),
                                        last_name=context.getSourcePersonLastName(),
                                        default_email_text=email_text,
                                        default_telephone_text=context.getSourcePersonDefaultTelephoneText())
    if organisation is None and context.getSourceOrganisationTitle():
      organisation_module = portal.getDefaultModule(organisation_portal_type)
      organisation = organisation_module.newContent(portal_type=organisation_portal_type,
                                                    title=context.getSourceOrganisationTitle())
      if person is None:
        organisation.setDefaultEmailText(email_text)
    if person is not None and organisation is not None and organisation.getRelativeUrl() not in person.getSubordinationList():
      subordination_list = person.getSubordinationList()
      subordination_list.append(organisation.getRelativeUrl())
      person.setDefaultCareerSubordinationList(subordination_list)
    if person is not None and portal_workflow.isTransitionPossible(person, 'validate'):
      person.validate(comment=translateString("Validated when ingesting ${event_reference}", mapping={"event_reference": context.getReference()}))
    if organisation is not None and portal_workflow.isTransitionPossible(organisation, 'validate'):
      organisation.validate(translateString("Validated when ingesting ${event_reference}", mapping={"event_reference": context.getReference()}))
    if person is not None:
      context.setSourceValue(person)
    elif organisation is not None:
      context.setSourceValue(organisation)
    else:
      raise ValueError('At least one Person or one Organisation must be set as sender')

  # Associate a ticket for incoming Web Messages from Contact-Us form

  ticket_portal_type = 'Support Request'
  ticket_module = portal.getDefaultModule(ticket_portal_type)

  ticket = ticket_module.newContent(portal_type=ticket_portal_type,
                                    causality_value=context,
                                    destination_decision=context.getSource(),
                                    resource=portal.portal_preferences.getPreferredSupportRequestResource(),
                                    source_section=portal.portal_preferences.getPreferredSection(),
                                    start_date=DateTime())
  # if event as no recipient read it from ticket
  if not context.hasDestination():
    context.setDestination(ticket.getSourceSection())

  # Associate ticket to current event
  follow_up_list = context.getFollowUpList()
  if ticket.getRelativeUrl() not in follow_up_list:
    follow_up_list.append(ticket.getRelativeUrl())
    context.setFollowUpList(follow_up_list)
  ticket.submit()

# BBB support 2 workflows
# event_workflow
if portal_workflow.isTransitionPossible(context, 'receive'):
  context.receive()
if len(context.getFollowUpList()) > 0 and \
   portal_workflow.isTransitionPossible(context, 'acknowledge_event'):
  portal_workflow.doActionFor(context, 'acknowledge_action',
                              create_event=False)

# event_simulation_workflow
if portal_workflow.isTransitionPossible(context, 'stop'):
  context.stop()
if portal_workflow.isTransitionPossible(context, 'deliver'):
  context.deliver()
