/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translate", "translate")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this,
        options = param_list[0];
      return gadget.jio_allDocs(options)
        .push(function (result) {
          var i, date, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("modification_date")) {
              date = new Date(result.data.rows[i].value.modification_date);
              result.data.rows[i].value.modification_date = {
                field_gadget_param: {
                  allow_empty_time: 0,
                  ampm_time_style: 0,
                  css_class: "date_field",
                  date_only: true,
                  description: "The Date",
                  editable: 1,
                  hidden: 0,
                  hidden_day_is_last_day: 0,
                  "default": date.toUTCString(),
                  key: "modification_date",
                  required: 0,
                  timezone_style: 0,
                  title: "Modification Date",
                  type: "DateTimeField"
                }
              };
            }
          }
          return result;
        });
    })

    .allowPublicAcquisition('updateHeader', function () {
      return;
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
          page_title: 'Search',
          page_icon: 'search',
          filter_action: true
        };

      return gadget.getUrlParameter('history')
        .push(function (result) {
          if (result !== undefined) {
            return gadget.getUrlFor({command: 'history_previous'});
          }
        })
        .push(function (selection_url) {
          if (selection_url === undefined) {
            return gadget.getUrlFor({command: 'display'});
          }
          header_dict.selection_url = selection_url;
        })
        .push(function (front_url) {
          if (front_url !== undefined) {
            header_dict.front_url = front_url;
          }
          return gadget.updateHeader(header_dict);
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter('extended_search'),
            gadget.getDeclaredGadget('form_list'),
            gadget.translate('What are you looking for?')
          ]);
        })
        .push(function (result_list) {
          var form_gadget = result_list[1],
            extended_search = result_list[0],
            translated_text = result_list[2],
            group_list = [],
            field_dict = {},
            column_list = [
              ['translated_portal_type', 'Type'],
              ['modification_date', 'Modification Date'],
              ['title', 'Title'],
              ['reference', 'Reference'],
              ['description', 'Description'],
              ['translated_validation_state_title', 'State']
            ];

          if (extended_search) {
            field_dict.listbox = {
              "column_list": column_list,
              "show_anchor": 0,
              "default_params": {},
              "editable": 1,
              "editable_column_list": [],
              "key": "field_listbox",
              "lines": 30,
              "list_method": "portal_catalog",
              "query": "urn:jio:allDocs?query=",
              "portal_type": [],
              "search_column_list": column_list,
              "sort_column_list": column_list,
              "sort": [],
              "title": "Documents",
              "type": "ListBox"
            };
            group_list.push([
              "bottom",
              [["listbox"]]
            ], [
              "hidden", ["listbox_modification_date"]
            ]);

          } else {
            field_dict.message = {
              default: translated_text,
              css_class: "",
              description: "",
              editable: 0,
              hidden: 0,
              key: "message",
              required: 0,
              title: "",
              type: "StringField"
            };
            group_list.push([
              "bottom",
              [["message"]]
            ]);
          }

          return form_gadget.render({
            erp5_document: {
              "_embedded": {
                "_view": field_dict
              },
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: group_list
            }
          });
        });
    });
}(window, rJS, RSVP));