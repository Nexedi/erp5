/*global window, RSVP, SimpleQuery, ComplexQuery, Query,
         ensureArray, Array*/
/*jslint indent: 2, maxerr: 3, nomen: true, unparam: true, continue: true */
(function (window, RSVP, SimpleQuery, ComplexQuery, Query,
           ensureArray, Array) {
  "use strict";

  ///////////////////////////////
  // Page title calculation
  ///////////////////////////////
  function calculateSynchronousPageTitle(gadget, erp5_document) {
    var title = erp5_document.title,
      portal_type = erp5_document._links.type.name,
      is_module = / (Module|Tool)$/.test(erp5_document._links.type.href),
      traversed_document_jio_key;

    if (erp5_document._links.hasOwnProperty('traversed_document')) {
      traversed_document_jio_key = erp5_document._links.traversed_document.name;
    }

    if ((!is_module) &&
        erp5_document.hasOwnProperty('_embedded') &&
        erp5_document._embedded.hasOwnProperty('_view') &&
        erp5_document._embedded._view.hasOwnProperty('_links') &&
        erp5_document._embedded._view._links.hasOwnProperty('traversed_document') &&
        traversed_document_jio_key === erp5_document._embedded._view._links.traversed_document.name) {
      // When refreshing the page (after Base_edit), only the form content is recalculated
      // and erp5_document.title may contain the old title value.
      // Get the title value from the calculated form if possible
      // No need to do this for module, which do not use Base_edit
      title = erp5_document._embedded._view._links.traversed_document.title;
    }
    if (is_module) {
      return title;
    }
    return portal_type + ': ' + title;
  }

  window.calculatePageTitle = function (gadget, erp5_document) {
    return new RSVP.Queue()
      .push(function () {
        return calculateSynchronousPageTitle(gadget, erp5_document);
      });
  };

  ///////////////////////////////
  // Form list navigation
  ///////////////////////////////
  window.renderFormViewHeader = function (gadget, jio_key, view, erp5_document,
                                          filter_action) {
    return new RSVP.Queue()
      .push(function () {
        var url_for_parameter_list = [
          {command: 'display_dialog_with_history', options: {
            jio_key: jio_key,
            page: "tab",
            view: view
          }},
          {command: 'display_dialog_with_history', options: {
            jio_key: jio_key,
            page: "action",
            view: view
          }},
          {command: 'history_previous'},
          {command: 'selection_previous'},
          {command: 'selection_next'},
          {command: 'display_dialog_with_history', options: {
            jio_key: jio_key,
            page: "export",
            view: view
          }},
          {command: 'change', options: {editable: true}}
        ];
        if (erp5_document._links.action_object_new_content_action) {
          url_for_parameter_list.push({command: 'display_dialog_with_history', options: {
            jio_key: jio_key,
            view: erp5_document._links.action_object_new_content_action.href,
            editable: true
          }});
        }
        return RSVP.all([
          gadget.isDesktopMedia(),
          gadget.getUrlParameter('selection_index'),
          gadget.getUrlForList(url_for_parameter_list)
        ]);
      })
      .push(function (result_list) {
        var url_list = result_list[2],
          header_dict = {
            edit_url: url_list[6],
            tab_url: url_list[0],
            actions_url: url_list[1],
            export_url: (
              erp5_document._links.action_object_jio_report ||
              erp5_document._links.action_object_jio_exchange ||
              erp5_document._links.action_object_jio_print
            ) ? url_list[5] : '',
            selection_url: url_list[2],
            // Only display previous/next links if url has a selection_index,
            // ie, if we can paginate the result list of the search
            previous_url: result_list[1] ? url_list[3] : '',
            next_url: result_list[1] ? url_list[4] : '',
            page_title: calculateSynchronousPageTitle(gadget, erp5_document)
          };
        if (result_list[0]) {
          header_dict.add_url = url_list[7] || '';
        }
        if (filter_action === true) {
          header_dict.filter_action = true;
        }
        return gadget.updateHeader(header_dict);
      });

  };

  ///////////////////////////////
  // Form list navigation
  ///////////////////////////////
  window.renderFormListHeader = function (gadget, jio_key, view, erp5_document) {
    var new_content_action = erp5_document._links.action_object_new_content_action,
      url_for_parameter_list = [
        {command: 'display_dialog_with_history', options: {
          jio_key: jio_key,
          page: "action",
          view: view
        }},
        {command: 'history_previous'},
        {command: 'display_dialog_with_history', options: {
          jio_key: jio_key,
          page: "export",
          view: view
        }}
      ];

    if (new_content_action !== undefined) {
      url_for_parameter_list.push({command: 'display_dialog_with_history', options: {
        jio_key: jio_key,
        view: new_content_action.href,
        editable: true
      }});
    }

    return gadget.getUrlForList(url_for_parameter_list)
      .push(function (url_list) {
        return gadget.updateHeader({
          panel_action: true,
          jump_url: "",
          fast_input_url: "",
          add_url: url_list[3] || '',
          actions_url: url_list[0],
          export_url: (
            erp5_document._links.action_object_jio_report ||
            erp5_document._links.action_object_jio_print ||
            erp5_document._links.action_object_jio_exchange
          ) ? url_list[2] : '',
          page_title: calculateSynchronousPageTitle(gadget, erp5_document),
          front_url: url_list[1],
          filter_action: true
        });
      });

  };

  ///////////////////////////////
  // Handle listbox action list
  ///////////////////////////////
  function mergeGlobalActionWithRawActionList(jio_key, view, jump_view,
                                              link_list, group_id_list,
                                              command_mapping,
                                              editable_mapping) {
    var i, j, group,
      action_type,
      current_href,
      class_name,
      extra_options,
      options,
      command,
      group_mapping = {},
      url_mapping = {},
      default_command_mapping = {
        "view": "display_with_history",
        "action_object_jio_jump": "display_dialog_with_history",
        "action_object_jio_action": "display_with_history_and_cancel",
        "action_object_view": "display_with_history",
        "action_workflow": "display_dialog_with_history",
        "action_object_clone_action": "display_with_history_and_cancel",
        "action_object_delete_action": "display_with_history_and_cancel"
      };

    editable_mapping = editable_mapping || {};
    command_mapping = command_mapping || {};

    function addRawUrlToGroupMapping(group, action_type) {
      var index;
      if (link_list.hasOwnProperty(action_type)) {
        if (!group_mapping.hasOwnProperty(group)) {
          group_mapping[group] = [];
        }
        if (link_list[action_type] instanceof Array) {
          for (index = 0; index < link_list[action_type].length; index += 1) {
            if (link_list[action_type][index].href) {
              link_list[action_type][index].action_type = action_type;
              group_mapping[group].push(link_list[action_type][index]);
            }
          }
        } else {
          link_list[action_type].action_type = action_type;
          group_mapping[group].push(link_list[action_type]);
        }
      }
    }

    for (i = 0; i < group_id_list.length; i += 1) {
      group = group_id_list[i];
      if (group instanceof Array) {
        action_type = group[0];
        group_mapping[action_type] = ensureArray(link_list[action_type]);
        addRawUrlToGroupMapping(action_type, action_type + "_raw");
        if (group.length > 1) {
          for (j = 1; j < group.length; j += 1) {
            if (link_list.hasOwnProperty(group[j])) {
              group_mapping[action_type] = group_mapping[
                action_type
              ].concat(
                ensureArray(link_list[group[j]])
              );
            }
            addRawUrlToGroupMapping(action_type,
                                    group[j] + "_raw");
          }
        }
      } else {
        group_mapping[group] = ensureArray(
          link_list[group]
        );
        addRawUrlToGroupMapping(group, group + "_raw");
      }
    }

    for (group in group_mapping) {
      if (group_mapping.hasOwnProperty(group)) {
        if (!url_mapping.hasOwnProperty(group)) {
          url_mapping[group] = [];
        }
        for (i = 0; i < group_mapping[group].length; i += 1) {
          class_name = "";
          current_href = group_mapping[group][i].href;
          if (view === 'view' && group_mapping[group][i].name === view) {
            class_name = 'active';
          } else if (current_href === view) {
            class_name = 'active';
          } else if (jump_view && ((current_href === jump_view) ||
              (current_href === view))) {
            class_name = 'active';
          }
          if (group_mapping[group][i].action_type &&
                group_mapping[group][i].action_type.indexOf("_raw") !== -1) {
            command = "raw";
            options = {
              url: group_mapping[group][i].href
            };
            extra_options = {
              title: group_mapping[group][i].title
            };
          } else {
            command = command_mapping[group] || default_command_mapping[group];
            options = {
              jio_key: jio_key,
              view: group_mapping[group][i].href,
              editable: editable_mapping[group]
            };
            extra_options = {
              title: group_mapping[group][i].title,
              class_name: class_name
            };
          }
          if (group === "view") {
            // Views in ERP5 must be forms but because of
            // OfficeJS we keep it empty for different default
            options.page = undefined;
          }

          extra_options.url_kw = {
            command: command,
            absolute_url: command === "raw" ? true : false,
            options: options
          };
          url_mapping[group].push(extra_options);
        }
      }
    }
    return url_mapping;
  }

  function getListboxClipboardActionList() {
    var action_list = ensureArray(this.state.erp5_document._links.action_object_list_action || []),
      i,
      result_list = [],
      icon;
    result_list.push({
      title: 'Copy',
      icon: 'copy',
      action: 'copy_document_list'
    });
    for (i = 0; i < action_list.length; i += 1) {
      if (action_list[i].name === 'delete_document_list') {
        icon = 'trash-o';
      } else if (action_list[i].name === 'paste_document_list') {
        icon = 'paste';
      } else {
        continue;
      }
      result_list.push({
        title: action_list[i].title,
        icon: icon,
        action: action_list[i].name
      });
    }
    return result_list;
  }

  function createSearchQuery(checked_uid_list, key) {
    var i,
      search_query,
      query_list = [];

    for (i = 0; i < checked_uid_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        type: "simple",
        operator: "=",
        value: checked_uid_list[i]
      }));
    }

    search_query = new ComplexQuery({
      operator: "OR",
      query_list: query_list,
      type: "complex"
    });
    return Query.objectToSearchText(search_query);
  }

  function notifyTranslatedMessage(gadget, options) {
    return gadget.getTranslationClipboardAction(options.message)
      .push(function (translated_message) {
        options.message = translated_message;
        return gadget.notifySubmittedClipboardAction(options);
      });
  }

  function triggerListboxClipboardAction(argument_list) {
    var gadget = this,
      action_list = ensureArray(gadget.state.erp5_document._links.action_object_list_action || []),
      action_name = argument_list[0],
      checked_uid_list = argument_list[1],
      unchecked_uid_list = argument_list[2],
      view,
      i,
      queue;

    if (checked_uid_list.length === 0) {
      // If nothing is checked, use all unchecked values (same as xhtml style)
      checked_uid_list = unchecked_uid_list;
    }

    if (action_name !== 'copy_document_list') {
      // Copy action is only done on javascript side
      for (i = 0; i < action_list.length; i += 1) {
        if (action_name === action_list[i].name) {
          view = action_list[i].href;
        }
      }
      if (view === undefined) {
        // Action was not found.
        return notifyTranslatedMessage(gadget, {
          "message": "Action not handled"
        });
      }
    }

    if (action_name === 'paste_document_list') {
      // Get the list of document uid from the internal clipboard
      queue = gadget.getSettingClipboardAction('clipboard')
        .push(function (uid_list) {
          checked_uid_list = uid_list || [];
        });
    } else {
      queue = new RSVP.Queue();
    }

    return queue
      .push(function () {
        if (checked_uid_list.length === 0) {
          // Do not trigger action if the listbox was empty
          // Dialog listbox use catalog method, which may be different from the current select method
          // and so, it is mandatory to propagate a list of uid, otherwise, the dialog may display
          // an unexpected huge list of unrelated documents
          return notifyTranslatedMessage(gadget, {
            "message": "Nothing selected"
          });
        }

        if (action_name === 'copy_document_list') {
          return gadget.setSettingClipboardAction('clipboard', checked_uid_list)
            .push(function () {
              return notifyTranslatedMessage(gadget, {
                "message": "Copied",
                "status": "success"
              });
            });
        }

        return gadget.redirectClipboardAction({
          command: 'display_dialog_with_history',
          options: {
            "jio_key": gadget.state.jio_key,
            "view": view,
            "extended_search": createSearchQuery(
              checked_uid_list,
              'catalog.uid'
            )
          }
        }, true);
      });
  }

  function declareGadgetClassCanHandleListboxClipboardAction(gadget_klass) {
    gadget_klass
      .declareAcquiredMethod("getTranslationClipboardAction", "translate")
      .declareAcquiredMethod("setSettingClipboardAction", "setSetting")
      .declareAcquiredMethod("getSettingClipboardAction", "getSetting")
      .declareAcquiredMethod("redirectClipboardAction", "redirect")
      .declareAcquiredMethod("notifySubmittedClipboardAction",
                             "notifySubmitted")
      // Handle listbox custom button
      .allowPublicAcquisition("getListboxClipboardActionList",
                              getListboxClipboardActionList)
      .allowPublicAcquisition("triggerListboxClipboardAction",
                              triggerListboxClipboardAction);
  }
  window.mergeGlobalActionWithRawActionList = mergeGlobalActionWithRawActionList;
  window.triggerListboxClipboardAction = triggerListboxClipboardAction;
  window.declareGadgetClassCanHandleListboxClipboardAction =
    declareGadgetClassCanHandleListboxClipboardAction;

}(window, RSVP, SimpleQuery, ComplexQuery, Query, ensureArray, Array));