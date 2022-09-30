from Products.ZSQLCatalog.SQLCatalog import SQLQuery

portal = context.getPortalObject()
resource = portal.restrictedTraverse(resource_relative_url)

base_contribution_uid_dict = {}
for base_contribution in base_contribution_list:
  base_contribution_uid_dict[base_contribution]= (
        portal.portal_categories.restrictedTraverse(
          base_contribution).getUid())


total_price = 0
total_quantity = 0

line_list = []

inventory_kw = dict(strict_base_contribution_uid=base_contribution_uid_dict.values(),
          section_category=context.getGroup(base=1),
          portal_type=portal_type,
          simulation_state=('stopped', 'delivered'),
          resource_uid=resource.getUid(),
          mirror_date=dict(query=context.getStopDate(), range='ngt'),
          only_accountable=False,
          parent_portal_type=delivery_portal_type)
if context.getValidationState() == 'validated':
  inventory_kw['default_aggregate_uid'] = context.getUid()
else:
  aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()
  inventory_kw['where_expression'] = SQLQuery('(SELECT COUNT(uid) from category where '
          'base_category_uid=%s and uid=stock.uid) = 0' % aggregate_base_category_uid)

for brain in context.portal_simulation.getMovementHistoryList(**inventory_kw):
  movement = brain.getObject()
  transaction = movement.getParentValue()
  is_source = movement.getSource() == brain.node_relative_url

  quantity = (brain.total_quantity or 0) * sign or 0
  price = (brain.total_price or 0) * sign or 0

  total_quantity += quantity
  total_price += price

  line_list.append(transaction.asContext(uid='new_',
                          title=movement.hasTitle() and
                                movement.getTitle() or
                                transaction.getTitle(),
                          reference=transaction.getReference(),
                          specific_reference=is_source and
                                              transaction.getSourceReference() or
                                              transaction.getDestinationReference(),
                          third_party_name=is_source and
                                           movement.getDestinationSectionTitle() or
                                           movement.getSourceSectionTitle(),
                          date=brain.date,
                          total_quantity=quantity,
                          total_price=price))

container.REQUEST.set('TaxReturn_getDetailReportSectionStat',
               dict(total_price=total_price, total_quantity=total_quantity))
return line_list
