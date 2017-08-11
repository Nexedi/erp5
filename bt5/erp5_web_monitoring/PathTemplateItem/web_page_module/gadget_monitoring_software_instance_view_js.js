/*global window, rJS, RSVP, Handlebars, loopEventListener, $, atob */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, Handlebars, loopEventListener, $, atob) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    hashCode = new Rusha().digestFromString;

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////

  function formatDate(d) {
    function addZero(n) {
      return n < 10 ? '0' + n : '' + n;
    }

    return d.getFullYear() + "-" + addZero(d.getMonth()+1)
      + "-" + addZero(d.getDate()) + " " + addZero(d.getHours())
      + ":" + addZero(d.getMinutes()) + ":" + addZero(d.getSeconds());
  }

  gadget_klass

    .setState({
      instance: "",
      promise_list: [],
      opml: "",
      opml_outline: "",
      jio_gadget: "",
      graph_gadget: "",
      breadcrumb_gadget: ""
    })
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (gadget) {
      gadget.property_dict = {
        render_deferred: RSVP.defer()
      };
    })

    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.property_dict.element = element;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_gadget")
        .push(function (graph_gadget) {
          return gadget.changeState({graph_gadget: graph_gadget});
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_gadget")
        .push(function (jio_gadget) {
          return gadget.changeState({jio_gadget: jio_gadget});
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("breadcrumb_gadget")
        .push(function (breadcrumb_gadget) {
          return gadget.changeState({breadcrumb_gadget: breadcrumb_gadget});
        });
    })
    /*.ready(function (gadget) {
      return gadget.getSetting('instance_overview_selection')
        .push(function (selection) {
          gadget.property_dict.selection = selection || '';
        });
    })*/

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (option_dict) {
      var gadget = this;

      return gadget.updateHeader({
        title: "Monitoring software instance view"
      })
        .push(function () {
          return gadget.jio_get(option_dict.key);
        })
        .push(function (current_document) {
          if (current_document.portal_type === "global") {
            return gadget.changeState({instance: current_document})
              .push(function () {
                // Get opml outline document
                return gadget.jio_allDocs({
                  select_list: [
                    "parent_url",
                    "parent_id",
                    "title",
                    "opml_title",
                    "reference"],
                  query: '(portal_type:"opml-outline") AND (reference:"' +
                    gadget.state.instance.parent_id + '")'
                });
              })
              .push(function (opml_outline) {
                return gadget.changeState({
                  opml_outline: opml_outline.data.rows[0].value
                });
              });
          }
          return gadget.changeState({opml_outline: current_document})
            .push(function (opml_outline) {
              return gadget.jio_allDocs({
                select_list: [
                  "_embedded",
                  "_links",
                  "data",
                  "date",
                  "reference",
                  "parent_id",
                  "state",
                  "title",
                  "status",
                  "hosting-title"
                ],
                query: '(portal_type:"global") AND (parent_id:"' +
                  current_document.reference + '")'
              });
            })
            .push(function (instance) {
              if (instance.data.total_rows > 0) {
                return gadget.changeState({
                  instance: instance.data.rows[0].value
                });
              }
              console.log("Cannot find document: " + option_dict.key);
              return {};
            });
        })
        .push(function () {
          return gadget.jio_allDocs({
              select_list: [
                "source",
                "lastBuildDate",
                "comments",
                "category",
                "reference"
              ],
              query: '(portal_type:"promise") AND (parent_id:"' +
                gadget.state.instance.parent_id + '")'
            });
        })
        .push(function (promise_result) {
          return gadget.changeState({promise_list: promise_result.data.rows});
        })
        .push(function () {
          return gadget.jio_allDocs({
            select_list: ["basic_login", "url", "title"],
            query: '(portal_type:"opml") AND (url:"' +
              gadget.state.opml_outline.parent_url + '")'
          });
        })
        .push(function (opml_doc) {
          return gadget.changeState({opml: opml_doc.data.rows[0].value});
        })
        .push(function () {
          return gadget.state.breadcrumb_gadget.render({
            icon: "cubes",
            url_list: [
              {
                title: gadget.state.opml.title,
                url: "#page=hosting_subscription_view&key=" +
                  gadget.state.opml.url
              },
              {
                title: gadget.state.instance.title,
              }
            ]
          });
        })
        .push(function () {
          var instance_content,
            promise_list_template,
            content,
            promise_content,
            promise_list = [],
            i,
            tmp_url,
            tmp_process_url,
            current_document = gadget.state.instance,
            pass_url = '',
            private_url = current_document._links
                .hasOwnProperty('private_url') ? current_document
                ._links.private_url.href : '';

          if (private_url !== '') {
            private_url = private_url.replace("jio_private", "private");
            pass_url = "https://" + atob(gadget.state.opml.basic_login) +
              "@" + private_url.split("//")[1];
          }
          gadget.property_dict.monitor = current_document;
          if (current_document.hasOwnProperty('data') &&
              current_document.data.hasOwnProperty('state')) {

            instance_content = Handlebars.compile(
              templater.getElementById("details-widget-overview").innerHTML
            ),
            promise_list_template = Handlebars.compile(
              templater.getElementById("promiselist-widget-template").innerHTML
            );

            // Resource view URLs
            tmp_url = "#page=resource_view&key=" + gadget.state.opml_outline.reference;
            tmp_process_url = "#page=process_view&key=" +
              gadget.state.opml_outline.reference;

            content = instance_content({
                title: current_document.title,
                date: current_document.date,
                status: current_document.status,
                error: current_document.state.error,
                success: current_document.state.success,
                instance: current_document._embedded.instance || '',
                public_url: current_document._links
                  .hasOwnProperty('public_url') ? current_document
                  ._links.public_url.href : '',
                private_url: pass_url,
                rss_url: current_document._links.hasOwnProperty('rss_url') ? current_document._links.rss_url.href : '',
                resource_url: tmp_url,
                process_url: tmp_process_url,
                warning: (current_document.status.toUpperCase() === "WARNING") ? true : false
              });

              for (i = 0; i < gadget.state.promise_list.length; i += 1) {
                promise_list.push({
                  date: formatDate(
                    new Date(gadget.state.promise_list[i].value.lastBuildDate)
                  ),
                  title: gadget.state.promise_list[i].value.source,
                  status: gadget.state.promise_list[i].value.category,
                  message: gadget.state.promise_list[i].value.comments || "No message output",
                  href: "#page=view&key=" + gadget.state.promise_list[i].value.reference
                });
                if (current_document.status === "WARNING") {
                  promise_list[i].status = current_document.status;
                }
              }
              promise_content = promise_list_template({
                promise_list: promise_list
              });
            gadget.property_dict.element.querySelector(".overview-details .content-details")
              .innerHTML = content;
            gadget.property_dict.element.querySelector(".promise-list")
              .innerHTML = promise_content;
            return $(gadget.property_dict.element.querySelectorAll('fieldset[data-role="controlgroup"]'))
              .controlgroup().controlgroup('refresh');
          }
          
        })
        .push(function () {
          return gadget.property_dict.render_deferred.resolve();
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.render_deferred.promise;
        })
        .push(function () {
          var jio_options = {
            type: "webhttp",
            url: gadget.state.instance._links.private_url.href
              .replace("jio_private", "private") +
              'documents/'.replace("jio_private", "private"),
            basic_login: gadget.state.opml.basic_login
          };
          $(".graph-full .signal").removeClass("ui-content-hidden");
          gadget.state.jio_gadget.createJio(jio_options);
          return gadget.state.jio_gadget.get(
            gadget.state.instance.data.state
          )
          .push(undefined, function (error) {
            console.log(error);
            return {};
          });
        })
        .push(function (element_dict) {
          var promise_data = [
              "Date, Success, Error, Warning",
              new Date() + ",0,0,0"
            ],
            data = element_dict.data || promise_data;

          $(".graph-full .signal").addClass("ui-content-hidden");
          return gadget.state.graph_gadget.render(
            data.join('\n'),
            {
              ylabel: '<span class="graph-label"><i class="fa fa-bar-chart"></i> Success/Failure count</span>',
              legend: 'always',
              labelsDivStyles: { 'textAlign': 'right' }
            },
            "customInteractionModel"
          );
        });
          //return RSVP.all(promise_list);
    });

}(window, rJS, RSVP, Handlebars, loopEventListener, $, atob));
