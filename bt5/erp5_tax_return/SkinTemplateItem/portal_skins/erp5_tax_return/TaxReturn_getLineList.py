from Products.ZSQLCatalog.SQLCatalog import SQLQuery
portal = context.getPortalObject()

line_list = []

tax_type_definition = context.portal_types[context.getPortalType()]

for tax_return_line in tax_type_definition.contentValues(
      portal_type='Tax Return Line',
      sort_on=('float_index',),):

  if tax_return_line.getProperty('total_price'):
    method = portal.portal_simulation.getInventoryAssetPrice
  else:
    method = portal.portal_simulation.getInventory

  inventory_kw = dict(
          section_category=context.getGroup(base=1),
          strict_base_contribution_uid=tax_return_line.getBaseContributionUidList(),
          portal_type=tax_return_line.getPropertyList('line_portal_type'),
          parent_portal_type=tax_return_line.getPropertyList('delivery_portal_type'),
          simulation_state=('stopped', 'delivered'),
          mirror_date=dict(query=context.getStopDate(), range='ngt'),
          only_accountable=tax_return_line.getProperty('only_accountable'),
          )

  if context.getValidationState() == 'validated':
    inventory_kw['default_aggregate_uid'] = context.getUid()
  else:
    aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()
    # TODO include context portal type
    inventory_kw['where_expression'] = SQLQuery('(SELECT COUNT(uid) from category where '
            'base_category_uid=%s and uid=stock.uid) = 0' % aggregate_base_category_uid)

  line_list.append(
      tax_return_line.asContext(
        getListItemUrl=lambda *args: None, # XXX we could leave the link for developer
        quantity=tax_return_line.getProperty('multiplier') * method(**inventory_kw)))

return line_list
