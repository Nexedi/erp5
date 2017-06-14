/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('getUrlFor', function (argument_list) {
      if (argument_list[0].command === 'index') {
        return this.getUrlFor({command: 'display_stored_state', options: {jio_key: argument_list[0].options.jio_key}});
      }
      return this.getUrlFor.apply(this, argument_list);
    })
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) && (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [['title', 'ascending']];
          }
          return result;
        });
    })
    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })
    .declareMethod("render", function () {
      var gadget = this,
        header_dict = {
          page_title: 'Modules',
          page_icon: 'puzzle-piece',
          filter_action: true
        };

      return gadget.updateHeader(header_dict)
        .push(function () {
          return gadget.getDeclaredGadget('form_list');
        })
        .push(function (form_gadget) {
          var column_list = [
            ['translated_title', 'Title']];
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "listbox": {
                "column_list": column_list,
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox",
                "lines": 1000,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=parent_uid%3A%220%22%20AND%20meta_type%3A%22ERP5%20Folder%22%20AND%20id%3A%22%25_module%22",
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "title": "Modules",
                "type": "ListBox"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
            form_definition: {
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        });
    });
}(window, rJS));