from builtins import str
from Products.ZSQLCatalog.SQLCatalog import SQLQuery
from Products.PythonScripts.standard import Object
from ZTUtils import make_query
portal = context.getPortalObject()

line_list = []

if total_price:
  method = context.portal_simulation.getInventoryAssetPrice
else:
  method = context.portal_simulation.getInventory

def URLGetter(section_title,
              base_contribution,
              resource_relative_url,
              multiplier,
              total_price):
  def getListItemUrl(alias, index, selection_name):
    if alias == 'resource_title':
      return '%s/view' % portal.restrictedTraverse(
                                resource_relative_url).absolute_url()
    return 'TaxReturn_viewDetailReportSection?%s' % make_query(
                              section_title=section_title,
                              base_contribution_list=[base_contribution],
                              resource_relative_url=resource_relative_url,
                              multiplier=multiplier,
                              portal_type=list(portal_type),
                              delivery_portal_type=list(delivery_portal_type),
                              journal=alias, # XXX
                              total_price=total_price,)
  return getListItemUrl

total = {}

base_contribution_uid_dict = {}
for base_contribution in base_contribution_list:
  base_contribution_uid_dict[base_contribution]= (
        portal.portal_categories.restrictedTraverse(
          base_contribution).getUid())

inventory_kw = dict(
        section_category=context.getGroup(base=1),
        strict_base_contribution_uid=list(base_contribution_uid_dict.values()),
        portal_type=portal_type,
        parent_portal_type=delivery_portal_type,
        simulation_state=('stopped', 'delivered'),
        mirror_date=dict(query=context.getStopDate(), range='ngt'),
        only_accountable=only_accountable,
        )

if context.getValidationState() == 'validated':
  inventory_kw['default_aggregate_uid'] = context.getUid()
else:
  aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()
  # TODO include context portal type
  inventory_kw['where_expression'] = SQLQuery('(SELECT COUNT(uid) from category where '
          'base_category_uid=%s and uid=stock.uid) = 0' % aggregate_base_category_uid)


# get all resources that have been used with this inventory parameters
resource_list = [brain.resource_relative_url for brain in
                  portal.portal_simulation.getInventoryList(
                        group_by_node=0,
                        group_by_section=0,
                        group_by_resource=1,
                        **inventory_kw)]

for resource_relative_url in resource_list:
  resource = portal.restrictedTraverse(resource_relative_url)
  inventory_kw['resource_uid'] = resource.getUid(),

  line_dict = dict(uid='new_',
                   resource_title=resource.getTranslatedTitle(),)

  for idx, base_contribution in enumerate(base_contribution_list):
    idx = str(idx)
    inventory_kw['strict_base_contribution_uid'] = base_contribution_uid_dict[base_contribution]
    amount = multiplier * method(**inventory_kw) or 0

    line_dict[idx] = amount
    line_dict['getListItemUrl'] = URLGetter(
        section_title=section_title,
        resource_relative_url=resource.getRelativeUrl(),
        base_contribution=base_contribution,
        multiplier=multiplier,
        total_price=total_price,)

    total[idx] = total.get(idx, 0) + amount

  line_list.append(Object(**line_dict))

line_list.sort(key=lambda line: line.resource_title)

container.REQUEST.set('TaxReturn_getSummaryReportSectionStat', total)
return line_list
