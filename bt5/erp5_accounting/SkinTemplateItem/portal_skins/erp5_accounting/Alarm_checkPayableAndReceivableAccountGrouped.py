"""Check that all transactions on payable and receivable accounts
that a 0 balance are grouped.

In other words, check that all transactions that can be grouped are grouped.
"""
from Products.CMFActivity.ActiveResult import ActiveResult
active_process = context.newActiveProcess()

portal = context.getPortalObject()

# Section category & strict have to be configured on alarm
section_category = context.getProperty('section_category')
assert section_category, "alarm not configured"
section_category_strict = context.getProperty('section_category_strict')

section_uid_list = portal.Base_getSectionUidListForSectionCategory(section_category, section_category_strict)
assert section_uid_list

precision = 3
section_currency = portal.Base_getCurrencyForSectionCategory(section_category, section_category_strict)
if section_currency:
  precision = context.getQuantityPrecisionFromResource(section_currency, precision)

search_params = dict(
    node_category=('account_type/asset/receivable',
                   'account_type/liability/payable'),
    section_uid=section_uid_list,
    simulation_state=('stopped', 'delivered'),
    portal_type=portal.getPortalAccountingMovementTypeList(),
    group_by_mirror_section=True,
    group_by_node=True,
    grouping_reference=None,
    )


for brain in portal.portal_simulation.getInventoryList(**search_params):
  if round(brain.total_price, precision) == 0:
    print('%s has a 0 balance but some not grouped transactions.' % brain.mirror_section_relative_url)
    if fixit:
      tr = brain.getObject().getParentValue()
      grouped_line_list = tr.AccountingTransaction_guessGroupedLines()
      if not grouped_line_list:
        # Group whatever can be grouped. XXX maybe we want to make this optional.
        grouped_line_list = tr.AccountingTransaction_guessGroupedLines(
          accounting_transaction_line_uid_list=[
            line.uid for line in portal.portal_simulation.getMovementHistoryList(
                                    node_uid=brain.node_uid,
                                    mirror_section_uid=brain.mirror_section_uid,
                                    section_uid=section_uid_list,
                                    simulation_state=('stopped', 'delivered'),
                                    portal_type=portal.getPortalAccountingMovementTypeList(),
                                    grouping_reference=None,) if not line.getObject().getGroupingReference()])
      if grouped_line_list:
        print('FIXED', grouped_line_list)
      else:
        print('NOT FIXED')

active_result = ActiveResult(
  summary=context.getTitle(),
  severity=str(printed) and 100 or 0,
  detail=printed,)

active_process.postResult(active_result)
