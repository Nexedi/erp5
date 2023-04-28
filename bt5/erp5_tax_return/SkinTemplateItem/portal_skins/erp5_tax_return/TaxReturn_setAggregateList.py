if REQUEST is not None:
  raise

portal = context.getPortalObject()
aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()

tag = 'tax_return_set_aggregate_%s' % context.getRelativeUrl()

for section_info in context.TaxReturn_getSectionInformationList():
  selection_params = section_info['selection_params']

  base_amount_uid_list = []
  for base_amount_relative_url in \
          selection_params['base_amount_relative_url_list']:
    base_amount_uid_list.append(
          portal.portal_categories.restrictedTraverse(
            base_amount_relative_url).getUid())

  # TODO: use section info instead of hardcoding portal types etc
  inventory_kw = dict(
        strict_base_contribution_uid=base_amount_uid_list,
        section_category=context.getGroup(base=1),
        portal_type='Invoice Line',
        simulation_state=('stopped', 'delivered'),
        only_accountable=False,
        mirror_date=dict(query=context.getStopDate(), range='ngt'),
        where_expression='(SELECT COUNT(uid) from category where '\
           'base_category_uid=%s and uid=stock.uid) = 0' % aggregate_base_category_uid,
        parent_portal_type=[journal[0] for journal in
                              selection_params['journal_list']])

  # TODO: distribute this
  for movement in portal.portal_simulation.getMovementHistoryList(**inventory_kw):
    movement.getObject().edit(activate_kw=dict(tag=tag),
                              aggregate_value=context)

context.activate(activity='SQLDict', after_tag=tag).getTitle()
