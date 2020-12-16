from Products.ERP5Type.Cache import CachingMethod

def getModuleActionInformationDict(**kw):
  Base_translateString = context.Base_translateString
  result_dict = {}

  # If the user is not allowed to get the category, return immediately.
  portal = context.getPortalObject()
  business_application = portal.restrictedTraverse('portal_categories/business_application',
                                                   None)
  if business_application is None:
    return result_dict

  renderCustomLink = portal.ERP5Site_renderCustomLink
  listFilteredActionsFor = portal.portal_actions.listFilteredActionsFor
  cancel_url = portal.absolute_url()

  # Use searchFolder, because security checks are required, and sorting
  # is not supported by listFolderContents.
  for o in business_application.searchFolder(sort_on='int_index'):
    module_category = o.getObject()
    module_list = module_category.getBusinessApplicationRelatedValueList(
                    checked_permission='View',
                    portal_type=portal.getPortalModuleTypeList())

    # It is necessary to sort the modules by translated titles for convenience.
    titled_module_list = [(module.getTranslatedTitle(), module) for module in module_list]
    titled_module_list.sort(key=lambda x: x[0])

    view_list = []
    add_list = []
    search_list = []
    exchange_list = []
    report_list = []
    print_list = []

    for translated_title, module in titled_module_list:
      module_url = module.absolute_url()
      action_dict = module.Base_filterDuplicateActions(listFilteredActionsFor(module))

      # Obtain a form id and a selection name from the view.
      # XXX Is it useful ?
      form_id = 'view'
      selection_name = 'default_selection'
      for ai in action_dict['object_view']:
        if ai['id'] == 'view':
          form_id = ai['url'].rsplit('/', 1)[-1]
          form = getattr(portal, form_id, None)
          if form is not None:
            listbox = form.Form_getListbox()
            if listbox is not None:
              selection_name = listbox.get_value('selection_name')
          break

      # Collect view actions.
      module_view_list = [(None, '%s/view' % module_url)]
      view_list.append((translated_title, module_view_list))

      # Collect add actions.
      module_add_list = []
      for content_type in module.getVisibleAllowedContentTypeList():
        action = 'add %s' % content_type
        url = renderCustomLink('%s/Base_doAction' % module_url,
                               dict(cancel_url=cancel_url,
                                    form_id=form_id,
                                    selection_name=selection_name,
                                    select_action=action))
        module_add_list.append((Base_translateString(content_type), url))
      for template in module.getDocumentTemplateList():
        action = 'template %s' % template.getRelativeUrl()
        url = renderCustomLink('%s/Base_doAction' % module_url,
                               dict(cancel_url=cancel_url,
                                    form_id=form_id,
                                    selection_name=selection_name,
                                    select_action=action))
        template_name = Base_translateString('${template_title} (Template)',
                                             mapping=dict(template_title=template.getTitle()))
        module_add_list.append((template_name, url))
      if module_add_list:
        add_list.append((translated_title, module_add_list))

      # Collect search actions.
      module_search_list = []
      for search_action in action_dict.get('object_search', ()):
        url = renderCustomLink(search_action['url'],
                               dict(cancel_url=cancel_url,
                                    form_id=form_id,
                                    selection_name=selection_name,
                                    dialog_category='object_search')).strip()
        module_search_list.append((Base_translateString(search_action['name']), url))
      if module_search_list:
        search_list.append((translated_title, module_search_list))

      # Collect exchange actions.
      module_exchange_list = []
      for exchange_action in action_dict.get('object_exchange', ()):
        url = renderCustomLink(exchange_action['url'],
                               dict(cancel_url=cancel_url,
                                    form_id=form_id,
                                    selection_name=selection_name,
                                    dialog_category='object_exchange')).strip()
        module_exchange_list.append((Base_translateString(exchange_action['name']), url))
      if module_exchange_list:
        exchange_list.append((translated_title, module_exchange_list))

      # Collect report actions.
      module_report_list = []
      for report_action in action_dict.get('object_report', ()):
        url = renderCustomLink(report_action['url'],
                               dict(cancel_url=cancel_url,
                                    form_id=form_id,
                                    selection_name=selection_name,
                                    dialog_category='object_report')).strip()
        module_report_list.append((Base_translateString(report_action['name']), url))
      if module_report_list:
        report_list.append((translated_title, module_report_list))

      # Collect print actions.
      module_print_list = []
      for print_action in action_dict.get('object_print', ()):
        url = renderCustomLink(print_action['url'],
                               dict(cancel_url=cancel_url,
                                    form_id=form_id,
                                    selection_name=selection_name,
                                    dialog_category='object_print')).strip()
        module_print_list.append((Base_translateString(print_action['name']), url))
      if module_print_list:
        print_list.append((translated_title, module_print_list))

    # Add the actions, only if they are not empty.
    for k, v in (('add', add_list), ('search', search_list),
                 ('exchange', exchange_list), ('report', report_list),
                 ('print', print_list), ('view', view_list)):
      if v:
        result_dict.setdefault(k, []).append((module_category.getTitle(), v))

  return result_dict

getModuleActionInformationDict = CachingMethod(getModuleActionInformationDict,
                                               id='ERP5Site_getModuleActionInformationDict',
                                               cache_factory='erp5_ui_long')

# those parameters are only used for the caching key
return getModuleActionInformationDict(
         user = context.portal_membership.getAuthenticatedMember().getId(),
         server_url = context.REQUEST.SERVER_URL,
         language = context.Localizer.get_selected_language())
