if REQUEST is not None:
  raise ValueError

if context.getPortalType() != "Expense Record":
  raise TypeError('%s is not supported' % context.getPortalType())

if not context.getDocId():
  # It means that sync is not finished yet.
  return

if not context.Base_isNewestVersionRecord(context):
  context.cancel(comment='Newer revision is found')
  return

portal = context.getPortalObject()
isTransitionPossible = portal.portal_workflow.isTransitionPossible
event = context

def markHistory(document, comment):
  portal_workflow = portal.portal_workflow
  last_workflow_item = portal_workflow.getInfoFor(ob=document,
                                                  name='comment',
                                                  wf_id='edit_workflow')
  if last_workflow_item != comment:
    portal_workflow.doActionFor(document, action='edit_action', comment=comment)

error = False

update_flag = False

if (event.getSimulationState() == "draft"):

  if context.portal_activities.countMessage(path=context.getPath(), method_id=script.id) > 1:
    return

  # Try to fetch person document. If none is found, do nothing.
  organisation = None
  person = event.getContributorValue()
  if (person is None):
    markHistory(event, "No owner person found")
    error = True
  if person is not None:
    organisation = person.getSubordinationValue()
    if (organisation is None):
      markHistory(event, "No subordination found for: %s" % person.getRelativeUrl())
      error = True

  from Products.ERP5Type.DateUtils import addToDate
  if date_now is None:
    date_now = DateTime()
  if context.Base_getDateTime(event.getDate()) > addToDate(date_now, day=31):
    markHistory(event, 'Date %s is a future date' % event.getDate())
    error = True
  elif context.Base_getDateTime(event.getDate()) < addToDate(date_now, day=-335):
    markHistory(event, 'Date %s is an old date' % event.getDate())
    error = True

  if error:
    context.changeToError()
    return


  # Document has been cloned and should be attached to an existing ticket
  ticket = None
  original_event = None
  if event.getCopyOf():
    original_event = context.Base_getValidOriginalEvent(event)
  if original_event is not None:

    ticket = original_event.getFollowUpValue()

    # Suspend original event if possible
    original_event.edit(
      visible_in_html5_app_flag=False,
    )
    if isTransitionPossible(original_event, 'deliver'):
      original_event.deliver(comment='New clone: %s' % event.getRelativeUrl())

    # Activate new event
    if isTransitionPossible(ticket, 'validate'):
      ticket.validate(comment='New clone: %s' % event.getRelativeUrl())
      ticket.suspend(comment='New clone: %s' % event.getRelativeUrl())

    # Update existing document
    update_flag = True

  if ticket is not None and update_flag:
    accounting_transaction = ticket.getSourceProjectValue()
    if not accounting_transaction.getSimulationState() in ('draft', 'planned'):
      raise ValueError('Accounting Transaction is no longer editable.')
  else:
    ticket = context.Base_createTicket(event)
    accounting_transaction = context.accounting_module.newContent(portal_type='Accounting Transaction')
  accounting_transaction.manage_delObjects(ids=list(accounting_transaction.objectIds()))

  account_dict = context.ExpenseRecord_getAccountDict(organisation)

  accounting_transaction.edit(
    title=event.getDocId(),
    comment=event.getComment(),
    source_section_value=organisation,
    destination_section_value=person,
    start_date=context.Base_getDateTime(event.getDate()),
    resource=context.getResource(),
    )
  accounting_transaction.newContent(portal_type='Accounting Transaction Line', source_value=account_dict['credit_account_value'], source_credit=context.getQuantity())
  accounting_transaction.newContent(portal_type='Accounting Transaction Line', source_value=account_dict['debit_account_value'], source_debit=context.getQuantity())
  accounting_transaction.newContent(id='photo', portal_type='Embedded File', data=context.getPhotoData().split(',')[1].decode('base64'))

  if accounting_transaction.getSimulationState() == 'draft':
    accounting_transaction.plan()

  ticket.edit(
    source_project_value=accounting_transaction,
    title='Accounting Transaction requested for: %s' % event.getTitle(),
    start_date=DateTime()
  )
  ticket.validate(comment='New automatic ticket from %s for %s' % (event.getRelativeUrl(), accounting_transaction.getRelativeUrl()))
  ticket.suspend(comment='New automatic ticket from %s for %s' % (event.getRelativeUrl(), accounting_transaction.getRelativeUrl()))

  # Prevent concurrent transaction to create 2 tickets for the same event
  event_kw = {
    'follow_up_value': ticket,
    'source_value': person,
    'source_section_value': organisation
  }
  event.edit(**event_kw)
  event.serializeSimulationState()

  if update_flag:
    event.stop(comment='Attached to existing ticket: %s' % ticket.getRelativeUrl())
  else:
    event.stop(comment='New automatic ticket: %s' % ticket.getRelativeUrl())

  return ticket, accounting_transaction
