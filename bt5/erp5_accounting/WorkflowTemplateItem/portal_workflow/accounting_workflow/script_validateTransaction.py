"""Validates the transaction for both source and destination section.

XXX why proxy role ???
"""
from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import translateString

transaction = state_change['object']

# XXX manually default start date to stop date
if not transaction.getStartDate() and transaction.getStopDate():
  transaction.setStartDate(transaction.getStopDate())

# XXX auto-fill mirror accounts, if necessary.
# We do not do it for internal invoice transaction, because we do it in
# only after starting the invoice, because this can make invoice not balanced
# for destination section, which is not a problem for source section accountant
# when starting.
# Using this in non-internal transaction is probably a bad idea.
if transaction.getPortalType() != 'Internal Invoice Transaction':
  transaction.AccountingTransaction_setDefaultMirrorAccountList()

# Check constraints
transaction.Base_checkConsistency()

# Check that the transaction is in an open accounting period when we validate
# it.
skip_period_validation = state_change['kwargs'].get(
                              'skip_period_validation', 0)
transition = state_change['transition']
if transition.id in ('plan_action', 'confirm_action') :
  skip_period_validation = 1

source_section = transaction.getSourceSectionValue(
                       portal_type=['Organisation', 'Person'])
destination_section = transaction.getDestinationSectionValue(
                       portal_type=['Organisation', 'Person'])

if source_section is None and destination_section is None:
  raise ValidationFailed(translateString('At least one section must be defined.'))

# check that no categories are used for section
if transaction.getSourceSectionValue(portal_type='Category') is not None or\
    transaction.getDestinationSectionValue(portal_type='Category') is not None:
  raise ValidationFailed(translateString('Using category for section is invalid.'))

transaction_line_list = transaction.getMovementList(
        portal_type=transaction.getPortalAccountingMovementTypeList())


def checkAccountingPeriodRecursivly(accounting_period, transaction_date):
  valid = accounting_period.getSimulationState() in ('planned', 'started')
  if not valid:
    return False
  for sub_accounting_period in accounting_period.contentValues():
    if sub_accounting_period.getSimulationState() in (
                                        'deleted', 'cancelled', 'draft'):
      continue
    if sub_accounting_period.getStartDate().earliestTime() <= \
            transaction_date <= \
            sub_accounting_period.getStopDate().latestTime():
      if not checkAccountingPeriodRecursivly(sub_accounting_period,
                                            transaction_date):
        return False
  return True

if not skip_period_validation :
  # check the date is in an opened period
  if source_section is not None:
    # if we don't have any accounts on this side, we don't enforce date checks
    valid_date = False
    no_accounts = True
    for line in transaction_line_list:
      if line.getSource(portal_type='Account'):
        no_accounts = False
    if no_accounts:
      valid_date = True
    else:
      section = source_section
      if section.getPortalType() == 'Organisation':
        section = section.Organisation_getMappingRelatedOrganisation()
      if not len(section.contentValues(
             filter=dict(portal_type="Accounting Period"))):
        valid_date = True
      else:
        accounting_period = transaction\
          .AccountingTransaction_getAccountingPeriodForSourceSection()
        transaction_date = transaction.getStartDate().earliestTime()
        valid_date = False
        if accounting_period is not None:
          valid_date = checkAccountingPeriodRecursivly(accounting_period,
                                                      transaction_date)

    if not valid_date:
      raise ValidationFailed(translateString("Date is not in a started Accounting Period "
                                             "for source section."))

  # do the same for destination section
  if destination_section is not None:
    # if we don't have any accounts on this side, we don't enforce date checks
    valid_date = False
    no_accounts = True
    for line in transaction_line_list:
      if line.getDestination(portal_type='Account'):
        no_accounts = False
    if no_accounts:
      valid_date = True
    else:
      section = destination_section
      if section.getPortalType() == 'Organisation':
        section = section.Organisation_getMappingRelatedOrganisation()
      if not len(section.contentValues(
             filter=dict(portal_type="Accounting Period"))):
        valid_date = True
      else:
        accounting_period = transaction\
          .AccountingTransaction_getAccountingPeriodForDestinationSection()
        transaction_date = transaction.getStopDate().earliestTime()
        valid_date = False
        if accounting_period is not None:
          valid_date = checkAccountingPeriodRecursivly(accounting_period,
                                                      transaction_date)

    if not valid_date:
      raise ValidationFailed(translateString("Date is not in a started Accounting Period "
                                             "for destination section."))
