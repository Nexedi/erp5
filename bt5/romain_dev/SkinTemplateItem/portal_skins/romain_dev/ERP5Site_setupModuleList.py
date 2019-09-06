portal = portal = context.getPortalObject()

module_business_application_map = {'base': ('currency_module',
                                            'organisation_module',
                                            'person_module',),
                                   'accounting': ('accounting_module',
                                                  'account_module',),
                                   'forge': ('bug_module', 'glossary_module', 'test_result_module', 'test_suite_module'),
                                   'dev': ('foo_module', 'bar_module', 'foo_bar_module'),
                                   'project': ('project_module', 'task_module', 'task_report_module'),
                                   'crm': ('campaign_module',
                                           'event_module',
                                           'meeting_module',
                                           'sale_opportunity_module',
                                           'support_request_module',),
                                   'dms': ('document_module',
                                           'image_module',
                                           'document_ingestion_module',
                                           'web_page_module',),
                                   'trade': ('internal_packing_list_module',
                                             'inventory_module',
                                             'purchase_order_module',
                                             'purchase_packing_list_module',
                                             'purchase_trade_condition_module',
                                             'returned_sale_packing_list_module',
                                             'sale_order_module',
                                             'sale_packing_list_module',
                                             'sale_trade_condition_module'),
                                   'pdm': ('component_module',
                                           'product_module',
                                           'purchase_supply_module',
                                           'sale_supply_module',
                                           'service_module',
                                           'transformation_module',),
                                   }

for business_application_category_id, module_ids in module_business_application_map.items():
  for module_id in module_ids:
    module = getattr(portal, module_id, None)
    if module is not None:
      module.edit(business_application = business_application_category_id)
return 'ok'
