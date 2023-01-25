from Products.ERP5Form.Report import ReportSection

portal = context.getPortalObject()
report_section_list = []

inventory_kw = dict(
        section_category=context.getGroup(base=1),
        portal_type='Invoice Line',
        simulation_state=('stopped', 'delivered'),
        mirror_date=dict(query=context.getStopDate(), range='ngt'),
        only_accountable=False,)

if context.getValidationState() == 'validated':
  inventory_kw['default_aggregate_uid'] = context.getUid()
else:
  aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()
  inventory_kw['where_expression'] = '(SELECT COUNT(uid) from category where '\
          'base_category_uid=%s and uid=stock.uid) = 0' % aggregate_base_category_uid

for section_info in context.TaxReturn_getSectionInformationList():
  section_title = section_info['section_title']
  common_selection_params = section_info['selection_params']
  base_amount_relative_url_list=common_selection_params['base_amount_relative_url_list']

  base_amount_uid_list = []
  for base_amount_relative_url in base_amount_relative_url_list:
    base_amount_uid_list.append(
          portal.portal_categories.restrictedTraverse(
            base_amount_relative_url).getUid())

  selection_params = dict(
                        section_title=section_title,
                        base_amount_relative_url_list=base_amount_relative_url_list,
                        sign=common_selection_params['sign'],
                        total_price=common_selection_params['total_price'], )

  for journal, journal_name in common_selection_params['journal_list']:
    # get all resources that have been used with this inventory parameters
    resource_list = [brain.resource_relative_url for brain in
                      portal.portal_simulation.getInventoryList(
                            group_by_node=0,
                            group_by_section=0,
                            group_by_resource=1,
                            parent_portal_type=journal,
                            strict_base_contribution_uid=base_amount_uid_list,
                            **inventory_kw)]

    for resource_relative_url in resource_list:
      resource = portal.restrictedTraverse(resource_relative_url)
      selection_params['journal'] = journal
      selection_params['resource_relative_url'] = resource.getRelativeUrl()
      selection_params['section_title'] = '%s (%s/%s)' % (section_title,
                                                          journal_name,
                                                          resource.getTranslatedTitle())
      report_section_list.append(ReportSection(
        path=context.getPhysicalPath(),
        form_id='TaxReturn_viewDetailReportSection',
        selection_name='tax_return_detail_report_section_selection',
        selection_params=selection_params.copy()))

return report_section_list
