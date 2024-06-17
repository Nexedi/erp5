/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i, j, tmp, value, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("lastBuildDate")) {
              result.data.rows[i].value.lastBuildDate = {
                field_gadget_param: {
                  //allow_empty_time: 0,
                  //ampm_time_style: 0,
                  css_class: "date_field",
                  date_only: 0,
                  description: "The Date",
                  editable: 0,
                  hidden: 0,
                  hidden_day_is_last_day: 0,
                  "default": result.data.rows[i].value.lastBuildDate,
                  key: "lastBuildDate",
                  required: 0,
                  timezone_style: 1,
                  title: "Promise Date",
                  type: "DateTimeField"
                }
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
            if (result.data.rows[i].value.hasOwnProperty("description")) {
              tmp = result.data.rows[i].value.description.split('\n');
              value = "";
              for (j = 1; j < tmp.length; j += 1) {
                // first line of text is the date and status
                if (!value && tmp[j].trim() !== "") {
                  value += tmp[j].slice(0, 50);
                  if (tmp[j].length >= 50 || j + 1 < tmp.length) {
                    // a part of text is not shown
                    value += "...";
                  }
                }
              }
              result.data.rows[i].value.description = value;
            }
            if (result.data.rows[i].value.hasOwnProperty("category")) {
              value = result.data.rows[i].value.category;
              result.data.rows[i].value.category = {
                field_gadget_param: {
                  css_class: "",
                  description: "The Status",
                  hidden: 0,
                  "default": value,
                  key: "category",
                  url: "gadget_erp5_field_status.html",
                  title: "Status",
                  type: "GadgetField"
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

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })
    .declareMethod("render", function (options) {
      return this.changeState({
        options: options,
        latest_reload_time: new Date().getTime()
      });
    })
    .onStateChange(function () {
      var gadget = this,
        lines_limit;

      return new RSVP.Queue()
        .push(function () {
          return gadget.getSetting("latest_sync_time");
        })
        .push(function (latest_sync_time) {
          if (latest_sync_time === undefined) {
            // no sync yet
            return gadget.redirect({command: "display", options: {page: "ojsm_import_export"}});
          }
        })
        .push(function () {
          return gadget.getSetting("listbox_lines_limit", 20);
        })
        .push(function (listbox_lines_limit) {
          lines_limit = listbox_lines_limit;
          return gadget.getDeclaredGadget('form_list');
        })
        .push(function (form_list) {
          var column_list = [
            ['category', 'Status'],
            ['source', 'Promise'],
            ['channel_item', 'Software Instance'],
            ['channel', 'Instance Tree'],
            ['lastBuildDate', 'Promise Date'],
            ['description', 'Message']
          ];
          return form_list.render({
            erp5_document: {
              "_embedded": {"_view": {
                "listbox": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 0,
                  "editable_column_list": [],
                  "key": "field_listbox",
                  "lines": lines_limit,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=portal_type%3A%22" +
                    "promise" + "%22",
                  "portal_type": [],
                  "search_column_list": column_list,
                  "sort_column_list": column_list,
                  "sort": [["category", "ascending"], ["channel", "ascending"]],
                  "title": "Monitoring Promises",
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
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: "Monitoring Promises Status",
            filter_action: true
          });
        });
    })

    .onLoop(function () {
      var gadget = this;

      return gadget.getSetting('latest_sync_time')
        .push(function (latest_sync_time) {
          if (latest_sync_time > gadget.state.latest_reload_time) {
            return gadget.changeState({latest_reload_time: new Date().getTime()});
          }
        });
    }, 30000);

}(window, rJS, RSVP));

