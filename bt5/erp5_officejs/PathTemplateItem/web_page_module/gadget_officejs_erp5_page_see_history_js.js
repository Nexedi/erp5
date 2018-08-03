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
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_toggleRevisionOption",
                           "jio_toggleRevisionOption")
    //.declareAcquiredMethod("getId")

    .setState({jio_key: undefined})

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this,
          jio_key,
          result;
      return gadget.jio_toggleRevisionOption(true)
        .push(function () {
          console.log(param_list[0]);
          console.log(gadget.state.jio_key);
          return gadget.jio_allDocs({query: "doc_id: " + gadget.state.jio_key);
        })
        .push(function (timestamps) {
          console.log("timestamps: ", timestamps);
          param_list[0].select_list.push(gadget.state.jio_key);
        })
        .push(function (res) {
          result = res;
          return gadget.jio_toggleRevisionOption(false);
        })
        .push(function () {
          console.log(result);
          var i, date, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("modification_date")) {
              date = new Date(result.data.rows[i].value.modification_date);
              result.data.rows[i].value.modification_date = {
                field_gadget_param: {
                  allow_empty_time: 0,
                  ampm_time_style: 0,
                  css_class: "date_field",
                  date_only: 0,
                  description: "The Date",
                  editable: 0,
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
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
          }
          return result;
        });
    })
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_list'),
            gadget.getSetting("portal_type"),
            gadget.changeState({jio_key: options.jio_key})
          ]);
        })
        .push(function (result) {
          console.log("result 1: ", result[1]);
          var column_list = [
            ['title', 'Title'],
            ['reference', 'Reference'],
            ['language', 'Language'],
            ['description', 'Description'],
            ['version', 'Version'],
            ['modification_date', 'Modification Date']
          ];
          return result[0].render({
            erp5_document: {
              "_embedded": {"_view": {
                "listbox": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 1,
                  "editable_column_list": [],
                  "key": "field_listbox",
                  "lines": 30,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=portal_type%3A%22" +
                    result[1] + "%22",
                  "portal_type": [],
                  "search_column_list": column_list,
                  "sort_column_list": column_list,
                  "sort": [['modification_date', 'descending']],
                  "title": "Documents",
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
            },
            jio_key: options.jio_key
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: "change", options: {"page": "ojs_add_document"}}),
            gadget.getSetting('document_title_plural'),
            gadget.getUrlFor({command: "change", options: {"page": "ojs_document_list"}})
          ]);
        })
        .push(function (result) {
          return gadget.updateHeader({
            page_title: result[1],
            filter_action: true,
            add_url: result[0],
            doc_list: result[2]
          });
        });
    });
}(window, rJS, RSVP));