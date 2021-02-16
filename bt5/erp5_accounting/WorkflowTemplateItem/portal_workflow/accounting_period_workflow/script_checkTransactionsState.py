from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import translateString

period = state_change['object']
portal = period.getPortalObject()

period.Base_checkConsistency()

# This tag is used in AccountingPeriod_createBalanceTransaction
if portal.portal_activities.countMessageWithTag('BalanceTransactionCreation'):
  raise ValidationFailed(translateString("Balance transaction creation already in progress. Please try again later."))

valid_simulation_state_list = ['cancelled', 'delivered', 'deleted', 'rejected']
all_state_list = [x[1] for x in
  portal.Base_getTranslatedWorkflowStateItemList(wf_id='accounting_workflow')]
invalid_simulation_state_list = [state for state in all_state_list
                                 if state not in valid_simulation_state_list]

if period.getParentValue().getPortalType() == 'Organisation':
  # if this is a "main" accounting period, we refuse to close if the previous
  # period is not already closed.
  for other_period in period.getParentValue().contentValues(
              portal_type='Accounting Period',
              checked_permission='View'):
    if other_period != period and \
       other_period.getSimulationState() not in ('delivered', 'cancelled') and\
       other_period.getStartDate() < period.getStartDate():
      raise ValidationFailed(translateString(
        "Previous accounting periods has to be closed first."))

section = period.getParentValue()
while section.getPortalType() == period.getPortalType():
  section = section.getParentValue()

section_category = section.getGroup(base=True)
if not section_category:
  raise ValidationFailed(translateString("This Organisation must be member of a Group"))


# XXX copy and paste from AccountingPeriod_createBalanceTransaction !
def isIndenpendantSection(section):
  for ap in section.contentValues(
              portal_type='Accounting Period',
              checked_permission='View'):
    if ap.getSimulationState() in ('started', 'stopped', 'delivered'):
      return True
  return False

def getDependantSectionList(group, main_section):
  section_list = []
  recurse = True
  for section in group.getGroupRelatedValueList(
                            portal_type='Organisation',
                            strict_membership=True,
                            checked_permission='View'):
    if section != main_section:
      if isIndenpendantSection(section):
        recurse = False
      else:
        section_list.append(section)
  if recurse:
    for subgroup in group.contentValues():
      section_list.extend(getDependantSectionList(subgroup, main_section))

  return section_list
# /XXX

section_uid = [section.getUid()] + [x.getUid() for x in getDependantSectionList(section.getGroupValue(), section)]


movement_list = portal.portal_simulation.getMovementHistoryList(
      section_uid=section_uid,
      from_date=period.getStartDate().earliestTime(),
      at_date=period.getStopDate().latestTime(),
      simulation_state=invalid_simulation_state_list,
      # We only consider accounting movements really using accounts as node.
      # There could be a line in stock table because the node is an organisation acquired
      # from parent invoice.
      node_uid=[node.uid for node in portal.portal_catalog(portal_type='Account')],
      portal_type=portal.getPortalAccountingMovementTypeList(),
      limit=1)

if movement_list:
  raise ValidationFailed(translateString(
    "All Accounting Transactions for this organisation during the period have to be closed first."))
