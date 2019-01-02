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
    // .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
/*
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
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
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter.apply(this, argument_list)
        .push(function (result) {
          if ((result === undefined) && (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [['modification_date', 'descending']];
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
*/
    .declareMethod("render", function (options) {
      var gadget = this,
        header_dict = {
          page_title: 'Select',
          // page_icon: 'select'
          // cancel_url: '#'
          // filter_action: false
        };
/*
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
*/
      return gadget.getUrlFor({
        command: 'history_previous'
      })
        .push(function (cancel_url) {
          header_dict.cancel_url = cancel_url;
          return gadget.updateHeader(header_dict);
        })
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('erp5_form'),
            gadget.getUrlParameter('listbox_json'),
            gadget.getUrlParameter('extended_search')
          ]);
        })
        .push(function (result_list) {
          return result_list[0].render({
            erp5_document: {"_embedded": {"_view": {
              "listbox": JSON.parse(result_list[1])
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
            form_definition: {
              extended_search: result_list[2],
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        });
    });
}(window, rJS));