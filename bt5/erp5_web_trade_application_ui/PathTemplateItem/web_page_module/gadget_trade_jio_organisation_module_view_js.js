/*globals window, RSVP, rJS, getWorkflowState*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })

    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) &&
               (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [['doc_id', 'descending']];
          }
          return result;
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getUrlFor({command: 'display', options:
            {jio_key: options.jio_key, page: "add_organisation"}});
        })
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "Organisation",
            right_url: url,
            right_title: "New"
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("form_list");
        })
        .push(function (form_gadget) {
          var column_list = [
            ['organisation_title', 'Title'],
            ['default_email_coordinate_text', 'Email'],
            ['default_telephone_coordinate_text', 'Telephone'],
            ['portal_type', 'Portal Type']
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
                "lines": 10,
                "list_method": "portal_catalog",
                "query": 'urn:jio:allDocs?query=' + 'portal_type:' +
                  '"Organisation"',
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "title": "Documents",
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
              ], ["hidden", ["listbox_modification_date"]]]
            }
          });

        });
    });

}(window, RSVP, rJS));