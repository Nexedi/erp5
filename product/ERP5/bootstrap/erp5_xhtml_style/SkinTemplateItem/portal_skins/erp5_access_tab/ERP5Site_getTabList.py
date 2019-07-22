def getTabList(status_dict, info_dict, add_all_tabs):
  tab_list = []
  basic_mode = status_dict.get('basic_mode', 1)
  dms_mode = status_dict.get('dms_mode', 1)
  express_mode = status_dict.get('express_mode', 1)

  if dms_mode or add_all_tabs:
    tab_list.append({'id': 'quick_search_tab',
                     'icon': 'tab_icon/access_search.png',
                     'renderer': 'ERP5Site_renderQuickSearchDialog',
                     'title': 'Quick Search'})

    tab_list.append({'id': 'contribution_tab',
                     'icon': 'tab_icon/share.png',
                     'renderer': 'ERP5Site_renderContributionDialog',
                     'title': 'Contribute'})

  if basic_mode or add_all_tabs:
    if info_dict.get('view') or add_all_tabs:
      tab_list.append({'id': 'browse_tab',
                       'icon': 'tab_icon/list.png',
                       'renderer': 'ERP5Site_renderViewActionList',
                       'title': 'Browse'})
    if info_dict.get('add') or add_all_tabs:
      tab_list.append({'id': 'document_creation_tab',
                       'icon': 'tab_icon/filenew.png',
                       'renderer': 'ERP5Site_renderDocumentCreationActionList',
                       'title': 'New'})

    if info_dict.get('search') or add_all_tabs:
      tab_list.append({'id': 'document_search_tab',
                       'icon': 'tab_icon/filefind.png',
                       'renderer': 'ERP5Site_renderDocumentSearchActionList',
                       'title': 'Dig'})

    if info_dict.get('report') or add_all_tabs:
      tab_list.append({'id': 'report_tab',
                       'icon': 'tab_icon/webexport.png',
                       'renderer': 'ERP5Site_renderReportActionList',
                       'title': 'Reports'})

    if info_dict.get('print') or add_all_tabs:
      tab_list.append({'id': 'printout_tab',
                       'icon': 'tab_icon/ps.png',
                       'renderer': 'ERP5Site_renderPrintActionList',
                       'title': 'Printouts'})

    if info_dict.get('exchange') or add_all_tabs:
      tab_list.append({'id': 'exchange_tab',
                       'icon': 'tab_icon/imp-exp.png',
                       'renderer': 'ERP5Site_renderExchangeActionList',
                       'title': 'Exchange'})

  if express_mode in ('support_enabled', 'advertisement_enabled') or add_all_tabs:
    tab_list.append({'id': 'express_support_tab',
                     'icon': 'tab_icon/support.png',
                     'renderer': 'ERP5Site_renderExpressSupport',
                     'title': 'Express Support'})
  return tab_list


status_dict = {}
info_dict = {}
if not add_all_tabs:
  # we have to calculate possible tabs
  status_dict = context.ERP5Site_getConfiguredStatusDict()
  info_dict = context.ERP5Site_getCategorizedModuleActionInformationDict()

return getTabList(status_dict = status_dict, \
                  info_dict = info_dict, \
                  add_all_tabs = add_all_tabs)
