"""Set grouping reference for selected lines.
Used as a fast input dialog action.
"""
from Products.CMFCore.WorkflowCore import WorkflowException
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
psm = Base_translateString('Nothing matches.')
request = container.REQUEST

# update selected uids 
portal.portal_selections.updateSelectionCheckedUidList(
    list_selection_name, uids=uids, listbox_uid=listbox_uid, REQUEST=request)
uids = portal.portal_selections.getSelectionCheckedUidsFor(list_selection_name)

# XXX when should it be validated ?
if node == '':
  node = context.REQUEST.get('field_your_node', node)
if mirror_section == '':
  mirror_section = context.REQUEST.get('field_your_mirror_section',
                                        mirror_section)
if grouping == '':
  grouping = request.get('your_grouping',
                         request.get('field_your_grouping',
                                     grouping))

# edit selection for dialog parameters
portal.portal_selections.setSelectionParamsFor(
              'grouping_reference_fast_input_selection',
              params=dict(node=node,
                          grouping=grouping,
                          mirror_section=mirror_section))

# calculate total selected amount 
total_selected_amount = 0
if uids:
  for line in portal.portal_catalog(uid=uids):
    line = line.getObject()
    if line.AccountingTransaction_isSourceView(): # XXX not optimal !
      total_selected_amount += (line.getSourceInventoriatedTotalAssetPrice() or 0)
    else:
      total_selected_amount += (line.getDestinationInventoriatedTotalAssetPrice() or 0)
request.set('total_selected_amount', total_selected_amount)

if update:
  context.Base_updateDialogForm(update=update)
  return context.Base_renderForm(
    'AccountingTransactionModule_viewGroupingFastInputDialog',
    REQUEST=request,
    keep_items={'portal_status_message': Base_translateString('Updated')}
  )

# otherwise, try to group...
if grouping == 'grouping':
  grouped_line_list = context.AccountingTransaction_guessGroupedLines(
                        accounting_transaction_line_uid_list=uids)
  if grouped_line_list:
    psm = Base_translateString('${grouped_line_count} lines grouped.',
                               mapping=dict(grouped_line_count=len(grouped_line_list)))

    # make sure nothing will be checked next time
    portal.portal_selections.setSelectionCheckedUidsFor(list_selection_name, [])

    # we check if we can mark some transaction as payed.
    transaction_list = {}
    for line in grouped_line_list:
      transaction_list[portal.restrictedTraverse(line).getParentValue()] = 1

    for transaction in transaction_list.keys():
      if transaction.getPortalType() == 'Balance Transfer Transaction':
        transaction = transaction.getCausalityValue()
      # Check if this document has a payment_state
      if getattr(transaction, 'getPaymentState', None) is not None:
        # if all [recievable|payable] lines were grouped, we can mark this
        # invoice as payed.
        cleared = 1

        line_list = transaction.getMovementList(
                       portal_type=portal.getPortalAccountingMovementTypeList())
        for btt in transaction.getCausalityRelatedValueList(
                           portal_type='Balance Transfer Transaction'):
          if btt.getSimulationState() == 'delivered':
            for btt_line in btt.getMovementList():
              line_list.append(btt_line)

        for line in line_list:
          if line.getParentValue().AccountingTransaction_isSourceView():
            account = line.getSourceValue(portal_type='Account')
          else:
            account = line.getDestinationValue(portal_type='Account')
          if account is not None and account.getAccountTypeId() in ( 'payable',
                                                                     'receivable' ):
            if line.getRelativeUrl() not in grouped_line_list:
              if not line.getGroupingReference():
                cleared = 0

        if cleared and transaction.getPaymentState() != 'cleared':
          if transaction.AccountingTransaction_isSourceView():
            date = transaction.getStartDate()
          else:
            date = transaction.getStopDate()
          # XXX specific !
          try:
            portal.portal_workflow.doActionFor(transaction, 'clear_action',
                                               payment_date=date)
          except WorkflowException:
            # Workflow action not supported
            pass

# or to ungroup based on how we are called.
else:
  assert grouping == 'ungrouping'
  # XXX is uids multi page safe here ?
  line_list = []
  if uids:
    line_list = [brain.getObject() for brain in portal.portal_catalog(uid=uids)]

  ungrouped_line_list = []
  for line in line_list:
    if line.getGroupingReference():
      # Call AccountingTransactionLine_resetGroupingReference synchronously
      # to know the number of ungrouped lines.
      ungrouped_line_list.extend(line.AccountingTransactionLine_resetGroupingReference(async=False))

  psm = Base_translateString('${ungrouped_line_count} lines ungrouped.',
                             mapping=dict(ungrouped_line_count=len(ungrouped_line_list)))

  # make sure nothing will be checked next time
  portal.portal_selections.setSelectionCheckedUidsFor(list_selection_name, [])

return context.Base_renderForm(
  'AccountingTransactionModule_viewGroupingFastInputDialog',
  REQUEST=request,
  keep_items={'portal_status_message': psm}
)
