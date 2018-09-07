/*global document, window, Option, rJS, RSVP, promiseEventListener, loopEventListener */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, promiseEventListener, loopEventListener) {
  "use strict";

  function getActionListByName(action_object, name) {
    // Usage:
    //   getActionListByName(erp5_document._links.action_object_view, "view")
    //   -> [{name: "view", ...}]
    //   getActionListByName(erp5_document._links.action_object_view, ["web_view", "view"])
    //   -> [{name: "web_view", ...}, {name: "view", ...}]
    //   getActionListByName(erp5_document._links.action_object_view, "not found")
    //   -> throws
    var iname = 0,
      iaction = 0,
      error_list = [],
      result = null;
    if (!(Array.isArray(action_object))) { action_object = [action_object]; }
    if (!(Array.isArray(name))) { name = [name]; }
    result = new Array(name.length);
    for (iname = 0; iname < name.length; iname += 1) {
      for (iaction = 0; iaction < action_object.length; iaction += 1) {
        if (name[iname] === action_object[iaction].name) {
          result[iname] = action_object[iaction];
          break;
        }
      }
      if (!result[iname]) { error_list.push(name[iname]); }
    }
    if (error_list.length) {
      throw new Error("getActionListByName: names not found: " + error_list.join(", "));
    }
    return result;
  }

  rJS(window)
    .ready(function (gadget) {
      gadget.property_dict = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.property_dict.element = element;
          gadget.property_dict.deferred = RSVP.defer();
        });
    })
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("updateConfiguration", "updateConfiguration")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .allowPublicAcquisition("updateHeader", function () {
      return;
    })
    .declareMethod('getSearchCriteria', function (name, seriesName) {
      var search_criteria, cur_mid_night = new Date(), days_2 = new Date(),
        days_7 = new Date(), days_30 = new Date(), begin_date, end_date;
      if (seriesName !== 'Support Request') {
        // Situation 1: Search Support Request with date.
        cur_mid_night.setHours(0, 0, 0, 0);
        cur_mid_night.setDate(cur_mid_night.getDate() + 1);

        days_2.setDate(cur_mid_night.getDate() - 2);
        days_7.setDate(cur_mid_night.getDate() - 7);
        days_30.setDate(cur_mid_night.getDate() - 30);
        days_2.setHours(0, 0, 0, 0);
        days_7.setHours(0, 0, 0, 0);
        days_30.setHours(0, 0, 0, 0);

        if (name === '< 2') {
          begin_date = days_2;
          cur_mid_night.setDate(cur_mid_night.getDate() + 1);
          end_date = cur_mid_night;
        } else if (name === '2-7') {
          begin_date = days_7;
          end_date = days_2;
        } else if (name === '7-30') {
          begin_date = days_30;
          end_date = days_7;
        } else {
          begin_date = new Date(1970, 1, 1);
          end_date = days_30;
        }
        // XXX do not translate here !
        search_criteria = '( translated_simulation_state_title: "' + seriesName + '" AND delivery.start_date: >= ' + begin_date.toISOString().slice(0, 10) + ' AND delivery.start_date: < ' + end_date.toISOString().slice(0, 10) + ' )';
      } else {
        // Situation 2: Search Support Request without date.
        search_criteria = '( translated_simulation_state_title: "' + name + '")';
      }
      return search_criteria;
    })
    .allowPublicAcquisition("chartItemClick", function (params) {
      var gadget = this;

      return gadget.getSearchCriteria(params[0][0], params[0][1])
        .push(function (result) {
          return gadget.redirect({command: 'change', options: {extended_search: result,
            field_listbox_begin_from: undefined}});
        })
        .push(undefined, function (error) {
          if (error instanceof RSVP.CancellationError) {
            return;
          }
          throw error;
        })
        .push(function () {
          var restore_filter_input = gadget.element.querySelectorAll("input")[2];
          restore_filter_input.disabled = false;
          restore_filter_input.classList.remove("ui-disabled");
        });
      // method code
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.changeState({
        render: true
      }).push(function () {
          return gadget.getDeclaredGadget("last")
            .push(function (listbox) {
              return listbox.render({
                jio_key: gadget.property_dict.option_dict.listbox_jio_key,
                view: gadget.property_dict.option_dict.listbox_gadget
              });
            });
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Customer Support Dashboard'
          });
        });
    })
    .declareJob("renderGraph", function () {
      var gadget = this,
        option_dict = gadget.property_dict.option_dict;
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          return RSVP.all([gadget.jio_getAttachment(
            'support_request_module',
            hateoas_url + 'support_request_module' +
              '/SupportRequest_getSupportRequestStatisticsAsJson'
          ),
            gadget.declareGadget(
              option_dict.graph_gadget,
              {
                scope: "graph",
                sandbox: "iframe",
                element: gadget.property_dict.element.querySelector("#wrap1")
              }
            ),
            gadget.declareGadget(
              option_dict.graph_gadget,
              {
                scope: "graph2",
                sandbox: "iframe",
                element: gadget.property_dict.element.querySelector("#wrap2")
              }
            )
            ]);
        })
        .push(function (result) {
          var bar_chart = document.getElementById("wrap1"),
            pie_chart = document.getElementById("wrap2"),
            loader = document.getElementsByClassName("graph-spinner");
          loader[0].style.display = "none";
          loader[1].style.display = "none";
          bar_chart.style.display = "block";
          pie_chart.style.display = "block";
          return result;
        })
        .push(function (result_list) {
          var sp_data = result_list[0], graph_gadget_1 = result_list[1], graph_gadget_2 = result_list[2];
          gadget.property_dict.graph_widget = graph_gadget_1;
          return RSVP.all([graph_gadget_1.render(
            {
              value: {
                data: [
                  {
                    value_dict: {
                      0: ["< 2", "2-7", "7-30", "> 30"],
                      1: [
                        sp_data.le2.validated,
                        sp_data['2to7'].validated,
                        sp_data['7to30'].validated,
                        sp_data.gt30.validated
                      ]
                    },
                    colors: ['#d48265'],
                    type: "bar",
                    title: "Opened"
                  },
                  {
                    value_dict: {
                      0: ["< 2", "2-7", "7-30", "> 30"],
                      1: [
                        sp_data.le2.submitted,
                        sp_data['2to7'].submitted,
                        sp_data['7to30'].submitted,
                        sp_data.gt30.submitted
                      ]
                    },
                    colors: ['#61a0a8'],
                    type: "bar",
                    title: "Submitted"
                  },
                  {
                    value_dict: {
                      0: ["< 2", "2-7", "7-30", "> 30"],
                      1: [
                        sp_data.le2.suspended,
                        sp_data['2to7'].suspended,
                        sp_data['7to30'].suspended,
                        sp_data.gt30.suspended
                      ]
                    },
                    colors: ['#c23531'],
                    type: "bar",
                    title: "Suspended"
                  }
                ],
                layout: {
                  axis_dict : {
                    '0': {"title": "Days"},
                    '1': {"title": "Number", "value_type": "number"}
                  },
                  title: "Support Request Pipe"
                }
              }
            }
          ),
            sp_data,
            graph_gadget_2
            ]);
        })
        .push(function (result_list) {
          var sp_data = result_list[1], graph_gadget = result_list[2];
          gadget.property_dict.graph_widget = graph_gadget;
          return graph_gadget.render({
            value:
              {
                data: [
                  {
                    value_dict: {
                      0: ["Opened", "Submitted", "Suspended", "Closed"],
                      1: [sp_data.validated, sp_data.submitted, sp_data.suspended, sp_data.invalidated]
                    },
                    colors: ['#d48265', '#61a0a8', '#c23531', '#2f4554'],
                    type: "pie",
                    title: "Support Request"
                  }
                ],
                layout: {
                  axis_dict : {
                    0: {"title": "date"},
                    1: {"title": "value",  "value_type": "number"}
                  },
                  title: "Last Month Activity"
                }
              }
          });
        });
    })
    .declareService(function () {
      var gadget = this,
        restore_filter_input = gadget.element.querySelectorAll("input")[2];
      return gadget.getUrlParameter('extended_search')
        .push(function (result) {
          if (result !== undefined) {
            restore_filter_input.disabled = false;
            restore_filter_input.classList.remove("ui-disabled");
          }
        });
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          var generate_rss_input = gadget.element.querySelectorAll("input")[1], /* XXX class based selectors ! */
            restore_filter_input = gadget.element.querySelectorAll("input")[2],
            one = new RSVP.Queue().push(function (){
              return promiseEventListener(generate_rss_input, "click", false);
            }).push(function () {
              generate_rss_input.disabled = true;
              generate_rss_input.classList.add("ui-disabled");
              return gadget.getSetting("hateoas_url")
                .push(function (hateoas_url) {
                  return gadget.jio_getAttachment(
                    'support_request_module',
                    hateoas_url + 'support_request_module'
                      + "/SupportRequestModule_generateRSSLinkAsJson"
                  );
                })
                .push(function (result) {
                  return gadget.translate("RSS Link").push(function(translated_rss_link_message) {
                    generate_rss_input.parentNode.href = result.restricted_access_url;
                    generate_rss_input.value = translated_rss_link_message, // "RSS Link";
                    generate_rss_input.disabled = false;
                    generate_rss_input.classList.remove("ui-disabled");
                  });
                });
            }),
            two = loopEventListener(restore_filter_input, "click", false, function () {
              restore_filter_input.disabled = true;
              restore_filter_input.classList.add("ui-disabled");
              return gadget.redirect({
                command: "change",
                options: {
                  extended_search: undefined,
                  field_listbox_begin_from: undefined
                }
              });
            }, true);

          generate_rss_input.disabled = false;
          generate_rss_input.classList.remove("ui-disabled");
          return RSVP.all([one, two]);
        });
    })
    .onStateChange(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment("support_request_module", "links"),
            gadget.getDeclaredGadget("worklist"),
            gadget.getUrlParameter('field_listbox_begin_from')
          ]);
        })
        .push(function (result_list) {
          var erp5_document = result_list[0],
            worklist_gadget = result_list[1],
            field_listbox_begin_from = result_list[2],
            view_list = erp5_document._links.action_object_view || [];

          gadget.property_dict.option_dict = {
            // graph_gadget: Keep ending slash to be consistent with the automatically set "base" tag
            graph_gadget: "unsafe/gadget_field_graph_echarts.html/",
            listbox_gadget: getActionListByName(view_list, "view_last_support_request")[0].href,
            listbox_jio_key: "support_request_module",
            field_listbox_begin_from: field_listbox_begin_from
          };

          return RSVP.all([
            worklist_gadget,
            gadget.renderGraph(), //Launched as service, not blocking
            gadget.getUrlFor({
              command: "display",
              options: {
                jio_key: "support_request_module",
                view: getActionListByName(view_list, "fast_input")[0].href,
                page: "support_request_fast_view_dialog"
              }
            })
          ]);
        })
        .push(function (result_list) {
          var worklist_gadget = result_list[0],
            create_sr_href = result_list[2],
            create_sr_input = gadget.element.querySelectorAll("input")[0];

          create_sr_input.parentNode.href = create_sr_href;
          create_sr_input.disabled = false;
          create_sr_input.classList.remove("ui-disabled");

          return worklist_gadget.render();
        });
    });

}(window, rJS, RSVP, promiseEventListener, loopEventListener));
