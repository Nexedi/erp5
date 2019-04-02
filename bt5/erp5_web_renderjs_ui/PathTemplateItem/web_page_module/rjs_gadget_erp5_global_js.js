/*global window, RSVP, Array, isNaN, SimpleQuery, ComplexQuery, Query,
         ensureArray */
/*jslint indent: 2, maxerr: 3, nomen: true, unparam: true, continue: true */
(function (window, RSVP, Array, isNaN, SimpleQuery, ComplexQuery, Query,
           ensureArray) {
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
  window.triggerListboxClipboardAction = triggerListboxClipboardAction;
  window.declareGadgetClassCanHandleListboxClipboardAction =
    declareGadgetClassCanHandleListboxClipboardAction;

}(window, RSVP, Array, isNaN, SimpleQuery, ComplexQuery, Query, ensureArray));