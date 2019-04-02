/*global window, RSVP, Array, isNaN, SimpleQuery, ComplexQuery, Query */
/*jslint indent: 2, maxerr: 3, nomen: true, unparam: true */
(function (window, RSVP, Array, isNaN, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  window.calculatePageTitle = function (gadget, erp5_document) {
    return new RSVP.Queue()
      .push(function () {
        var title = erp5_document.title,
          portal_type = erp5_document._links.type.name;
        if (/ Module$/.test(erp5_document._links.type.href)) {
          return portal_type;
        }
        return portal_type + ': ' + title;
      });
  };

  ///////////////////////////////
  // Handle listbox action list
  ///////////////////////////////
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

  function triggerListboxClipboardAction(argument_list) {
    var action_list = ensureArray(this.state.erp5_document._links.action_object_list_action || []),
      action_name = argument_list[0],
      checked_uid_list = argument_list[1],
      unchecked_uid_list = argument_list[2],
      gadget = this,
      extended_search = '',
      view,
      i;

    if (action_name === 'copy_document_list') {
      if (checked_uid_list.length === 0) {
        // If nothing is checked, use all unchecked values (same as xhtml style)
        checked_uid_list = unchecked_uid_list;
      }
      if (checked_uid_list.length === 0) {
        // XXX Queries do not correctly handle empty uid list
        return gadget.redirect({
          command: 'reload'
        });
      }
      return gadget.setSetting('clipboard', checked_uid_list)
        .push(function () {
          return gadget.notifySubmitted({
            "message": "Copied.",
            "status": "success"
          });
        });
    }

    for (i = 0; i < action_list.length; i += 1) {
      if (action_name === action_list[i].name) {
        view = action_list[i].href;
      }
    }

    if (checked_uid_list.length !== 0) {
      // If nothing is checked, use original query
      extended_search = createSearchQuery(
        checked_uid_list,
        'catalog.uid'
      );
    }

    if (view === undefined) {
      // Action was not found.
      // Reload
      return gadget.redirect({
        command: 'reload'
      });
    }

    if (action_name === 'paste_document_list') {
      return gadget.getSetting('clipboard')
        .push(function (uid_list) {
          uid_list = uid_list || [];
          if (uid_list.length === 0) {
            // Nothing to paste, go away
            uid_list = ['XXX'];
          }
          return gadget.redirect({
            command: 'display_dialog_with_history',
            options: {
              "jio_key": gadget.state.jio_key,
              "view": view,
              "extended_search": createSearchQuery(
                uid_list,
                'catalog.uid'
              )
            }
          }, true);
        });
    }

    return gadget.redirect({
      command: 'display_dialog_with_history',
      options: {
        "jio_key": gadget.state.jio_key,
        "view": view,
        "extended_search": extended_search
      }
    }, true);
  }
  window.triggerListboxClipboardAction = triggerListboxClipboardAction;

}(window, RSVP, Array, isNaN, SimpleQuery, ComplexQuery, Query));
