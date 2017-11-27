if lineCallback is None:
  lineCallback = lambda brain, period_name, line_dict: line_dict
if reportCallback is None:
  reportCallback = lambda x: x
traverse = context.getPortalObject().restrictedTraverse
account_number_memo = {}
def getAccountNumber(account_url):
  try:
    return account_number_memo[account_url]
  except KeyError:
    account_number_memo[account_url] = traverse(account_url).Account_getGapId()
  return account_number_memo[account_url]
def myLineCallback(brain, period_name, line_dict):
  line_dict = lineCallback(brain=brain, period_name=period_name, line_dict=line_dict)
  if line_dict is None:
    return
  movement = brain.getObject()
  transaction = movement.getParentValue()
  # Detailed version of the aged balance report needs to get properties from
  # the movement or transactions, but summary does not. This conditional is
  # here so that we do not load objects when running in summary mode.
  line_dict['explanation_title'] = movement.hasTitle() and movement.getTitle() or transaction.getTitle()
  line_dict['reference'] = transaction.getReference()
  line_dict['portal_type'] = transaction.getTranslatedPortalType()
  line_dict['date'] = brain.date
  if brain.mirror_section_uid == movement.getSourceSectionUid() and brain.mirror_node_uid == movement.getSourceUid():
    line_dict['specific_reference'] = transaction.getDestinationReference()
    line_dict['gap_id'] = getAccountNumber(movement.getDestination())
  else:
    line_dict['specific_reference'] = transaction.getSourceReference()
    line_dict['gap_id'] = getAccountNumber(movement.getSource())
    assert brain.mirror_section_uid == movement.getDestinationSectionUid()
  return line_dict
def myReportCallback(line_list):
  return reportCallback(
    sorted(
      line_list,
      key=lambda x: (x['mirror_section_title'], x['date'], x['explanation_title']),
    ),
  )
return context.AccountingTransactionModule_getAgedBalanceLineList(
  lineCallback=myLineCallback,
  reportCallback=myReportCallback,
  **kw
)
