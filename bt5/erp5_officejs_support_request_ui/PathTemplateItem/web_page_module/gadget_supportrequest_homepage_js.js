/*global document, window, Option, rJS, RSVP, Chart*/
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
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("updateConfiguration", "updateConfiguration")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .allowPublicAcquisition("updateHeader", function () {
      return;
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment("support_request_module", "links"),
            gadget.getDeclaredGadget("last")
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

          return RSVP.all([
            result_list[1].render({
              jio_key: "support_request_module",
              view: last_href
            })
          ]);
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Support Requests Home Page'
          });
        });
    })
    .declareService(function () {
      var gadget = this;
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          return gadget.jio_getAttachment(
            'support_request_module',
            hateoas_url + 'support_request_module'
              + "/SupportRequest_getSupportRequestStatisticsAsJson"
          );
        })
        .push(function (result) {
          new Chart(document.getElementById("bar-chart-grouped"), {
            type: 'bar',
            data: {
              labels: ["Less than 2 days", "2-7 days", "7-30 days", "More than 30 days"],
              datasets: [
                {
                  label: "Opened",
                  backgroundColor: "#3e95cd",
                  data: [
                    result.le2.validated,
                    result['2to7'].validated,
                    result['7to30'].validated,
                    result.gt30.validated
                  ]
                },
                {
                  label: "Submitted",
                  backgroundColor: "#e8c3b9",
                  data: [
                    result.le2.submitted,
                    result['2to7'].submitted,
                    result['7to30'].submitted,
                    result.gt30.submitted
                  ]
                },
                {
                  label: "Suspended",
                  backgroundColor: "#3cba9f",
                  data: [
                    result.le2.suspended,
                    result['2to7'].suspended,
                    result['7to30'].suspended,
                    result.gt30.suspended
                  ]
                },
                {
                  label: "Closed",
                  backgroundColor: "#8e5ea2",
                  data: [
                    result.le2.invalidated,
                    result['2to7'].invalidated,
                    result['7to30'].invalidated,
                    result.gt30.invalidated
                  ]
                }
              ]
            },
            options: {
              responsive : true,
              title: {
                display: true,
                text: 'Support Requests activities'
              }
            }
          });
          new Chart(document.getElementById("pie-chart"), {
            type: 'pie',
            data: {
              labels: ["Opened", "Closed", "Suspended", "Submitted"],
              datasets: [{
                label: "All Support Requests Status",
                backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9"],
                data: [result.validated, result.invalidated, result.suspended, result.submitted]
              }]
            },
            options: {
              responsive : true,
              title: {
                display: true,
                text: 'Support Requests state since last 30 days'
              }
            }
          });
        });
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
              editable: true,
              page: 'support_request_fast_view_dialog'
            }
          });
        })
        .push(function (url) {
          window.location.href = url;
        });
    });

}(window, rJS, RSVP));