/*global document, window, Option, rJS, RSVP*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

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
        search_criteria = '( translated_simulation_state_title: "' + seriesName + '" AND modification_date: >= ' + begin_date.toISOString().slice(0, 10) + ' AND modification_date: < ' + end_date.toISOString().slice(0, 10) + ' )';
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
          return gadget.redirect({command: 'change', options: {extended_search: result}});
        })
        .push(undefined, function (error) {
          if (error instanceof RSVP.CancellationError) {
            return;
          }
          throw error;
        })
        .push(function () {
          var restore = document.getElementById("restoreButton");
          restore.removeAttribute('disabled');
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
      })
        .push(function () {
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
            hateoas_url + 'support_request_module'
              + "/SupportRequest_getSupportRequestStatisticsAsJson"
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
                scope: "graph",
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
    .onStateChange(function () {
      var gadget = this,
        queue = new RSVP.Queue();

      queue
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment("support_request_module", "links"),
            gadget.getDeclaredGadget("worklist"),
            gadget.getUrlParameter('field_listbox_begin_from')
          ]);
        })
        .push(function (result_list) {
          var i,
            erp5_document = result_list[0],
            view_list = erp5_document._links.action_object_view || [],
            last_href;

          if (view_list.constructor !== Array) {
            view_list = [view_list];
          }

          for (i = 0; i < view_list.length; i += 1) {
            if (view_list[i].name === 'view_last_support_request') {
              last_href = view_list[i].href;
            }
          }

          if (last_href === undefined) {
            throw new Error('Cant find the list document view');
          }
          gadget.property_dict.option_dict = {
            graph_gadget: "unsafe/gadget_field_graph_echarts.html",
            listbox_gadget: last_href,
            listbox_jio_key: "support_request_module",
            field_listbox_begin_from: result_list[2]
          };

          return RSVP.all([
            result_list[1].render(),
            gadget.renderGraph() //Launched as service, not blocking
          ]);
        });
      return queue;
    })
    .onEvent('change', function (evt) {
      if (evt.target.id === "field_your_project") {
        var gadget = this;
        return gadget.getSetting("hateoas_url")
          .push(function (hateoas_url) {
            return gadget.jio_getAttachment(
              'support_request_module',
              hateoas_url + 'support_request_module'
                + "/SupportRequest_getSupportTypeList"
                + "?project_id=" + evt.target.value + "&json_flag=True"
            );
          })
          .push(function (sp_list) {
            var i,
              j,
              sp_select = document.getElementById('field_your_resource');
            for (i = sp_select.options.length - 1; i >= 0; i -= 1) {
              sp_select.remove(i);
            }

            for (j = 0; j < sp_list.length; j += 1) {
              sp_select.options[j] = new Option(sp_list[j][0], sp_list[j][1]);
            }
          });
      }
    }, false, false)
    .onEvent('click', function (event) {
      var gadget = this, rss_link = gadget.element.querySelector("#generate-rss"),
        generate_button = gadget.element.querySelector("#generateRSS"),
        restore = document.getElementById("restoreButton");

      if (event.target.id === "restoreButton") {
        restore.setAttribute("disabled", "disabled");

        return gadget.getDeclaredGadget("last")
          .push(function (listbox) {
            return listbox.render({
              jio_key: gadget.property_dict.option_dict.listbox_jio_key,
              view: gadget.property_dict.option_dict.listbox_gadget,
              extended_search: null
            });
          });
      }

      if (event.target.id === "generateRSS") {
        if (rss_link.getAttribute("href") === '#') {
          return gadget.getSetting("hateoas_url")
            .push(function (hateoas_url) {
              return gadget.jio_getAttachment(
                'support_request_module',
                hateoas_url + 'support_request_module'
                  + "/SupportRequestModule_generateRSSLinkAsJson"
              )
                .push(function (result) {
                  rss_link.href = result.restricted_access_url;
                  rss_link.style.display = "inline-block";
                  generate_button.style.display = "none";
                });
            });
        }
      } else if (event.target.id === "createSR") {
        return gadget.jio_getAttachment('support_request_module', 'links')
          .push(function (links) {
            var fast_create_url = links._links.view[2].href;
            return gadget.getUrlFor({
              command: 'display',
              options: {
                jio_key: "support_request_module",
                view: fast_create_url,
                page: 'support_request_fast_view_dialog'
              }
            });
          })
          .push(function (url) {
            window.location.href = url;
          });
      }
      event.returnValue = true;
    })
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.jio_getAttachment('support_request_module', 'links')
        .push(function (links) {
          var fast_create_url = links._links.view[2].href;
          return gadget.getUrlFor({
            command: 'display',
            options: {
              jio_key: "support_request_module",
              view: fast_create_url,
              page: 'support_request_fast_view_dialog'
            }
          });
        })
        .push(function (url) {
          window.location.href = url;
        });
    });

}(window, rJS, RSVP));
