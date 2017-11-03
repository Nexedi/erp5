/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
   /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i,
            len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            result.data.rows[i].value.connected =
              result.data.rows[i].value.connected ? '✓' : '';
            result.data.rows[i].value.notification =
              result.data.rows[i].value.notification ? '✓' : '';
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
      var gadget = this;

      return gadget.getUrlFor({
        command: 'change',
        options: {page: "jabberclient_new_contact"}
      })
        .push(function (url) {
          return gadget.updateHeader({
            page_title: 'Contacts',
            page_icon: 'puzzle-piece',
            filter_action: true,
            add_url: url
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget('form_list');
        })
        .push(function (form_gadget) {
          var column_list = [
            ['jid', 'Name'],
            ['notification', 'Notification'],
            ['connected', 'Connected']
          ];
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "listbox": {
                "column_list": column_list,
                "show_anchor": 0,
                "default_params": {},
                "editable": 0,
                "editable_column_list": [],
                "key": "field_listbox",
                "lines": 20,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs",
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "sort": [['notification', 'descending'], ['connected', 'descending'], ['jid', 'ascending']],
                "title": "Contacts",
                "type": "ListBox"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
              },
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