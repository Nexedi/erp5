/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  var gadget_klass = rJS(window);

  function getHostingData(gadget, filter) {
    // optimized way to fetch hosting subscription list
    var hosting_dict = {},
      instance_dict = {},
      total_rows = 0;
    return gadget.jio_allDocs(filter)
      .push(function (result) {
        var i;
        total_rows = result.data.total_rows;
        for (i = 0; i < result.data.total_rows; i += 1) {
          hosting_dict[result.data.rows[i].id] = {
            id: result.data.rows[i].id,
            value: {
              url: result.data.rows[i].value.url,
              status: "WARNING",
              date: 'Not Synchronized',
              title: result.data.rows[i].value.title,
              amount: 0
            }
          };
        }
        return gadget.jio_allDocs({
          query: '(portal_type:"opml-outline") OR (portal_type:"Software Instance")',
          select_list: [
            "parent_url",
            "status",
            "parent_id",
            "date",
            "portal_type"
          ]
        });
      })
      .push(function (result) {
        var i,
          key,
          item,
          row_list = [];
        for (i = 0; i < result.data.total_rows; i += 1) {
          if (result.data.rows[i].value.portal_type === 'opml-outline') {
            if (hosting_dict.hasOwnProperty(result.data.rows[i].value.parent_url)) {
              instance_dict[result.data.rows[i].id] = {
                parent_id: result.data.rows[i].value.parent_url
              };
            }
          }
        }
        for (i = 0; i < result.data.total_rows; i += 1) {
          if (result.data.rows[i].value.portal_type === 'Software Instance') {
            if (instance_dict.hasOwnProperty(result.data.rows[i].value.parent_id)) {
              instance_dict[result.data.rows[i].value.parent_id].date =
                result.data.rows[i].value.date;
              instance_dict[result.data.rows[i].value.parent_id].status =
                result.data.rows[i].value.status;
            }
          }
        }
        //calculate hosting subscription status
        for (key in instance_dict) {
          if (instance_dict.hasOwnProperty(key)) {
            item = hosting_dict[instance_dict[key].parent_id].value;
            item.amount += 1;
            if (item.status !== "ERROR") {
              item.status = instance_dict[key].status || "WARNING";
            }
            item.date = instance_dict[key].date || 'Not Synchronized';
            item.synced = item.status !== "WARNING" ? "YES" : "NO";
          }
        }
        for (key in hosting_dict) {
          if (hosting_dict.hasOwnProperty(key)) {
            row_list.push(hosting_dict[key]);
          }
        }
        return {data: {total_rows: total_rows, rows: row_list}};
      });
  }

  gadget_klass
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("renderApplication", "renderApplication")
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')

    .allowPublicAcquisition("getUrlFor", function (param_list) {
      if (param_list[0].options.jio_key !== undefined &&
          param_list[0].options.query.indexOf('portal_type:"opml"') !== -1) {
        param_list[0].options.page = "ojsm_hosting_subscription_view";
        param_list[0].options.opml_key = param_list[0].options.jio_key;
      }
      return this.getUrlFor(param_list[0]);
    })

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return getHostingData(gadget, param_list[0])
        .push(function (result) {
          var i,
            len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("date")) {
              result.data.rows[i].value.date = {
                allow_empty_time: 0,
                ampm_time_style: 0,
                css_class: "date_field",
                date_only: 0,
                description: "The Date",
                editable: 0,
                hidden: 0,
                hidden_day_is_last_day: 0,
                "default": new Date(result.data.rows[i].value.date).toUTCString(),
                key: "date",
                required: 0,
                timezone_style: 0,
                title: "Status Date",
                type: "DateTimeField"
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
            if (result.data.rows[i].value.hasOwnProperty("status")) {
              result.data.rows[i].value.status = {
                css_class: "",
                description: "The Status",
                hidden: 0,
                "default": result.data.rows[i].value.status,
                key: "status",
                url: "gadget_erp5_field_status.html",
                title: "Status",
                type: "GadgetField"
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
          return gadget.getSetting("listbox_lines_limit", 20);
        })
        .push(function (listbox_lines_limit) {
          lines_limit = listbox_lines_limit;
          return gadget.getDeclaredGadget('form_list');
        })
        .push(function (form_list) {
          var column_list = [
            ['status', 'Status'],
            ['title', 'Hosting Subscription'],
            ['amount', 'Instance Amount'],
            ['date', 'Status Date'],
            ['synced', 'Synced?']
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
                  "key": "hosting_subscription_listbox",
                  "lines": lines_limit,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=%28portal_type%3A%22" +
                    "opml" + "%22%29AND%28active%3A%22" +
                    "true" + "%22%29",
                  "portal_type": [],
                  "search_column_list": [['title', 'Hosting Subscription']],
                  "sort_column_list": [['title', 'Hosting Subscription']],
                  "sort": [["title", "ascending"]],
                  "title": "Hosting Subscriptions",
                  "command": "index",
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
            page_title: "Hosting Subscriptions Status",
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