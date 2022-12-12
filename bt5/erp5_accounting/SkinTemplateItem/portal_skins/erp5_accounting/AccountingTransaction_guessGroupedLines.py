"""Guess a grouping references for lines whose uids are passed as
accounting_transaction_line_uid_list.
If accounting_transaction_line_uid_list is not passed, this script assumes that
it's called on the context of an accounting transaction and it guess the grouping
of related accounting transactions using causality.
"""
import collections
from Products.ERP5Type.Utils import int2letter

# this dict associates (node, section, mirror_section, extra_grouping_parameter) to a list of
# accounting lines info (total_price, date and path)
lines_per_node = {}

# this counter associates the lines to the count of entities that are
# impacted by this accounting line.
# Typically it is 1 if the line is only for source/destination like in
# "normal" invoices and it can be 2 for Internal Invoices.
# When we found a match that can be grouped, we decrement this counter for
# this line. If all lines of the group have a 0 count, we can set grouping
# reference. This is a way to set grouping reference when the group is only
# valid for one side, it has to be valid for both side.
non_grouped_section_count = collections.Counter()

portal = context.getPortalObject()

if portal.portal_preferences.getPreference(
    'preferred_grouping_with_different_quantities', False):
  return

accounting_transaction_line_value_list = []
if accounting_transaction_line_uid_list is None:
  for accounting_transaction in context\
        .AccountingTransaction_getCausalityGroupedAccountingTransactionList():
    if accounting_transaction.getSimulationState()  not in ('stopped', 'delivered') and\
                          accounting_transaction.getUid() != context.getUid():
      continue
    for line in accounting_transaction.getMovementList(
        portal.getPortalAccountingMovementTypeList()):
      if line.getGroupingReference():
        continue
      accounting_transaction_line_value_list.append(line)
else:
  if accounting_transaction_line_uid_list:
    accounting_transaction_line_value_list = [
      brain.getObject() for brain in portal.portal_catalog(
        uid=accounting_transaction_line_uid_list)
    ]

for line in accounting_transaction_line_value_list:
  # source
  node_relative_url = line.getSource(portal_type='Account')
  if node_relative_url:
    section_relative_url = None
    source_section = line.getSourceSectionValue(portal_type='Organisation')
    if source_section is not None:
      source_section = \
        source_section.Organisation_getMappingRelatedOrganisation()
      section_relative_url = source_section.getRelativeUrl()

    line_relative_url = line.getRelativeUrl()
    non_grouped_section_count.update({line_relative_url: 1})
    lines_per_node.setdefault(
      (
        node_relative_url,
        section_relative_url,
        line.getDestinationSection(),
        line.AccountingTransactionLine_getGroupingExtraParameterList(
          source=True),
      ), []).append(
        dict(
          total_price=line.getSourceInventoriatedTotalAssetPrice() or 0,
          date=line.getStartDate(),
          path=line_relative_url))

  # destination
  node_relative_url = line.getDestination(portal_type='Account')
  if node_relative_url:
    section_relative_url = None
    destination_section = line.getDestinationSectionValue(
      portal_type='Organisation')
    if destination_section is not None:
      destination_section = \
        destination_section.Organisation_getMappingRelatedOrganisation()
      section_relative_url = destination_section.getRelativeUrl()
    line_relative_url = line.getRelativeUrl()
    non_grouped_section_count.update({line_relative_url: 1})
    lines_per_node.setdefault(
      (
        node_relative_url,
        section_relative_url,
        line.getSourceSection(),
        line.AccountingTransactionLine_getGroupingExtraParameterList(
          source=False),
      ), []).append(
        dict(
          total_price=line.getDestinationInventoriatedTotalAssetPrice() or 0,
          date=line.getStopDate(),
          path=line_relative_url))

# We do two passes, a first pass to check if lines are groupable from both
# sides in case of internal invoices - then a second path to actually set
# grouping references on groups that were groupable from both sides.
for (
    node,
    section,
    mirror_section,
    _,
), line_info_list in list(lines_per_node.items()):
  assert node
  # get the currency rounding for this section, with a fallback that something that would
  # allow grouping in case precision is not defined.
  currency_precision = 5
  if section:
    default_currency = portal.restrictedTraverse(
      section).getPriceCurrencyValue()
    if default_currency is not None:
      currency_precision = default_currency.getQuantityPrecision()
  total_price = round(
    sum([l['total_price'] for l in line_info_list]), currency_precision)
  if total_price == 0:
    for line in line_info_list:
      non_grouped_section_count.subtract({line['path']: 1})
  else:
    # this group is not valid, remove it for second path
    del lines_per_node[node, section, mirror_section, _]

changed_line_set = set()
for (
    node,
    section,
    mirror_section,
    _,
), line_info_list in lines_per_node.items():
  del node # not used, but necessary to separate lines for different nodes

  if sum(non_grouped_section_count[line['path']] for line in line_info_list) == 0:

    # we should include mirror node in the id_group, but this would reset
    # id generators and generate grouping references that were already used.
    id_group = ('grouping_reference', node, section, mirror_section)
    previous_default = context.portal_ids.getLastGeneratedId(
      id_group=id_group, default=0)
    grouping_reference = portal.portal_ids.generateNewId(
      id_generator='uid', id_group=id_group, default=previous_default + 1)

    # convert from int to letters
    string_reference = int2letter(grouping_reference)

    # get the grouping date
    date = max([line['date'] for line in line_info_list])

    for line in line_info_list:
      if line['path'] in changed_line_set:
        continue
      line_obj = portal.restrictedTraverse(line['path'])
      assert not line_obj.getGroupingReference(), line
      line_obj.setGroupingReference(string_reference)
      line_obj.setGroupingDate(date)
      line_obj.reindexObject(
        activate_kw=dict(tag='accounting_grouping_reference'))
      changed_line_set.add(line['path'])

return changed_line_set
