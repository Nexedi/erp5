/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    //.declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    /*.allowPublicAcquisition('updateHeader', function () {
      return;
    })*/
    .allowPublicAcquisition('getUrlForList', function (argument_list) {
      var i,
      options_list = argument_list[0],
      result_list = [];
      for (i = 0; i < options_list.length; i += 1) {
        if (options_list[i].command === 'index') {
          result_list.push({
            command: 'index',
            options: {jio_key: options_list[i].options.jio_key, page: "data_set"}
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
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_list')
        .push(function (form_gadget) {
          var column_list = [
            ['title', 'Title'],
            ['reference', 'Reference'],
            ['version', 'Version ']
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
                "query": "urn:jio:allDocs?query=portal_type%3A%22Data+Set%22+AND+validation_state%3A%22validated%22+AND+NOT+reference%3A%22%25_invalid%22",
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "sort": [['modification_date', 'descending']],
                "title": "Data Sets",
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
        })
        .push(function () {
          return gadget.getDeclaredGadget("download_access");
        })
        .push(function (my_gadget) {
          return my_gadget.render();
        });
    });
}(window, rJS));