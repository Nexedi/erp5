/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('getUrlForList', function (argument_list) {
      var i,
      options_list = argument_list[0],
      result_list = [];
      for (i = 0; i < options_list.length; i += 1) {
        if (options_list[i].command === 'index') {
          result_list.push({
            command: 'index',
            options: {jio_key: options_list[i].options.jio_key, page: "file_fif"}
          });
        } else {
          result_list.push(options_list[i]);
        }
      }
      return this.getUrlForList.apply(this, [result_list]);
    })
    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this,
        dataset = (options) ? options.reference : "",
        header_dict = {
          page_title: 'Files',
          filter_action: true
        };
      return gadget.getDeclaredGadget('form_list')
      .push(function (form_gadget) {
        var column_list = [
          ['title', 'Title'],
          ['reference', 'Reference'],
          ['size', 'Size (in bytes)']
        ];
        return form_gadget.render({
          erp5_document: {"_embedded": {"_view": {
            "listbox": {
              "column_list": column_list,
              "show_anchor": 0,
              "default_params": {},
              "editable": 1,
              "editable_column_list": [],
              "key": "field_listbox",
              "lines": 15,
              "list_method": "portal_catalog",
              "query": "urn:jio:allDocs?query=portal_type%3A%22Data+Stream%22+AND+validation_state%3A%22validated%22+AND+reference%3A%22" + dataset + "%2F%25%22",
              "portal_type": [],
              "search_column_list": column_list,
              "sort_column_list": column_list,
              "title": "Files",
              "sort": [['modification_date', 'descending']],
              "type": "ListBox"
            }
          }},
            "_links": {
              "type": {
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