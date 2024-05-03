/*global window, rJS, jIO, FormData, AbortController, RSVP, navigator */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  rJS(window)

    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("setSetting", "setSetting")

    .declareMethod('jio_allDocs', function (param_list, gadget) {
      var jio_gadget;
      if (param_list[0].query.indexOf('portal_type:"Promise"') !== -1 &&
          gadget.state.doc && gadget.state.doc.source) {
        return new RSVP.Queue()
          .push(function () {
            return gadget.declareGadget('gadget_officejs_monitoring_jio.html');
          })
          .push(function (result) {
            jio_gadget = result;
            return jio_gadget.createJio({
              type: "webhttp",
              // XXX fix of url
              url: gadget.state.doc.source_url.replace("jio_public", "public")
            });
          })
          .push(function () {
            // get history file on live
            return jio_gadget.get(
              gadget.state.doc.source + ".history"
            )
              .push(undefined, function (error) {
                if (error.name === "cancel") {
                  return undefined;
                }
                return gadget.notifySubmitted({
                  status: "error",
                  message: "Failed to get promise history content! \n" +
                    error.message || ''
                })
                  .push(function () {
                    return undefined;
                  });
              })
              .push(function (status_history) {
                var i, len, start, result = {};
                result.data = {rows: [], total_rows: 0};

                function addUTCTimezone(date_string) {
                  if (new RegExp(/[+-][\d]{2}\:?[\d]{2}$/).test(date_string)) {
                    return date_string;
                  }
                  return date_string + "+0000";
                }

                if (status_history && status_history.hasOwnProperty('data')) {
                  // the status history list is reversed ([old, ...., newest])
                  len = status_history.data.length;
                  start = len - param_list[0].limit[0] - 1;
                  if (start < 0) {
                    start = len - 1;
                  }
                  for (i = start; i >= 0; i -= 1) {
                    result.data.total_rows += 1;
                    result.data.rows.push({
                      value: {
                        status: {
                          field_gadget_param: {
                            css_class: "",
                            description: "The Status",
                            hidden: 0,
                            "default": status_history.data[i].status,
                            key: "status",
                            url: "gadget_erp5_field_status.html",
                            title: "Status",
                            type: "GadgetField"
                          }
                        },
                        start_date: {
                          field_gadget_param: {
                            allow_empty_time: 0,
                            ampm_time_style: 0,
                            css_class: "date_field",
                            date_only: 0,
                            description: "The Date",
                            editable: 0,
                            hidden: 0,
                            hidden_day_is_last_day: 0,
                            "default": addUTCTimezone(status_history.data[i].date ||
                              status_history.data[i]['start-date']),
                            key: "start_date",
                            required: 0,
                            timezone_style: 1,
                            title: "Date",
                            type: "DateTimeField"
                          }
                        },
                        change_date:  {
                          field_gadget_param: {
                            allow_empty_time: 0,
                            ampm_time_style: 0,
                            css_class: "date_field",
                            date_only: 0,
                            description: "The Date",
                            editable: 0,
                            hidden: 0,
                            hidden_day_is_last_day: 0,
                            "default": addUTCTimezone(status_history.data[i]['change-date'] ||
                              new Date(status_history.data[i]['change-time'] * 1000)
                              .toUTCString()),
                            key: "change_date",
                            required: 0,
                            timezone_style: 1,
                            title: "Status Date",
                            type: "DateTimeField"
                          }
                        },
                        message: status_history.data[i].message,
                        "listbox_uid:list": {
                          key: "listbox_uid:list",
                          value: 2713
                        }
                      }
                    });
                  }
                }
                return result;
              });
          });
      }
    });

}(window, rJS, jIO));