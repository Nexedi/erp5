/*global window, rJS, RSVP, Handlebars, $
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, Handlebars, RSVP, $) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    promise_widget_template = Handlebars.compile(
      templater.getElementById("promise-widget-template").innerHTML
    ),
    instance_widget_template = Handlebars.compile(
      templater.getElementById("pinstance-widget-template").innerHTML
    ),
    links_widget_template = Handlebars.compile(
      templater.getElementById("plinks-widget-template").innerHTML
    ),
    history_widget_template = Handlebars.compile(
      templater.getElementById("phistory-widget-template").innerHTML
    ),
    load_history_template = Handlebars.compile(
      templater.getElementById("load-history-template").innerHTML
    );

  function formatDate(d){
    function addZero(n){
      return n < 10 ? '0' + n : '' + n;
    }

    return d.getFullYear() + "-" + addZero(d.getMonth()+1)
      + "-" + addZero(d.getDate()) + " " + addZero(d.getHours())
      + ":" + addZero(d.getMinutes()) + ":" + addZero(d.getSeconds());
  }

  gadget_klass
    .setState({
      jio_gadget: "",
      promise: "",
      opml_outline: "",
      opml: "",
      instance: "",
      breadcrumb_gadget: ""
    })
    .ready(function (gadget) {
      gadget.property_dict = {
        render_deferred: RSVP.defer()
      };
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_gadget")
        .push(function (jio_gadget) {
          return gadget.changeState({"jio_gadget": jio_gadget});
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("breadcrumb_gadget")
        .push(function (breadcrumb_gadget) {
          return gadget.changeState({breadcrumb_gadget: breadcrumb_gadget});
        });
    })
    /*.ready(function (gadget) {
      return gadget.getDeclaredGadget("chart0")
        .push(function (chart0) {
          gadget.property_dict.chart0 = chart0;
        });
    })*/
    /*.ready(function (gadget) {
      return gadget.getDeclaredGadget("chart1")
        .push(function (chart1) {
          gadget.property_dict.chart1 = chart1;
        });
    })*/
    .declareMethod('render', function (options) {
      var gadget = this,
        global_state,
        url_options = $.extend(true, {}, options);
        url_options.t = Date.now() / 1000 | 0;
      return gadget.getUrlFor(url_options)
        .push(function (refresh_url) {
          //var back_url = '#page=main&t=' + (Date.now() / 1000 | 0);
          return RSVP.all([
            gadget.updateHeader({
              title: 'Monitoring Promise View',
              //back_url: back_url,
              //panel_action: false,
              refresh_url: refresh_url
            })
          ]);
        })
        .push(function () {
          return gadget.jio_get(options.key);
        })
        .push(function (promise_document) {
          return gadget.changeState({promise: promise_document});
        })
        .push(function () {
          // Get opml_document
          return gadget.jio_allDocs({
            select_list: [
              "parent_url",
              "parent_id",
              "title",
              "opml_title",
              "portal_type",
              "_links",
              "_embedded",
              "state",
              "status",
              "reference",
              "date"
            ],
            query: '((portal_type:"opml-outline") AND (reference:"' +
              gadget.state.promise.parent_id + '")) OR' +
              '((portal_type:"global") AND (parent_id:"' +
              gadget.state.promise.parent_id + '"))'
          }, function (error) {
            console.log(error);
            return {};
          });
        })
        .push(function (result_list) {
          var promise_list = [],
            i;
          for (i = 0; i < result_list.data.total_rows; i += 1) {
            if (result_list.data.rows[i].value.portal_type === "opml-outline") {
              promise_list.push(gadget.changeState({
                opml_outline: result_list.data.rows[i].value
              }));
            } else {
              promise_list.push(gadget.changeState({
                instance: result_list.data.rows[i].value
              }));
            }
          }
          return RSVP.all(promise_list);
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
            icon: "check-square",
            url_list: [
              {
                title: gadget.state.opml.title,
                url: "#page=hosting_subscription_view&key=" +
                  gadget.state.opml.url
              },
              {
                title: gadget.state.instance.title,
                url: "#page=software_instance_view&key=" +
                  gadget.state.instance.reference,
              },
              {
                title: gadget.state.promise.source,
              }
            ]
          });
        })
        .push(function () {
          var content,
            element,
            promise_list = [],
            instance_content,
            links_content,
            amount = 0,
            history_content,
            pass_url = '';

          // fix URLs
          gadget.state.instance._links.private_url.href = gadget.state.instance.
            _links.private_url.href.replace("jio_private", "private");
          gadget.state.instance._links.public_url.href = gadget.state.instance.
            _links.public_url.href.replace("jio_public", "public");
          pass_url = "https://" + atob(gadget.state.opml.basic_login) +
            "@" + gadget.state.instance._links.private_url.href.split("//")[1];

          element = {
            status: gadget.state.promise.category,
            status_date: formatDate(new Date(gadget.state.promise.pubDate)),
            title: gadget.state.promise.source,
            "start-date": formatDate(new Date(gadget.state.promise.lastBuildDate)),
            message: gadget.state.promise.comments,
            warning: (gadget.state.promise.category === "WARNING") ? true : false
          };
          gadget.property_dict.promise_dict = element;

          element.state = (element.status.toLowerCase() === 'error') ? 
            'red' : (element.status.toLowerCase() === 'warning') ? 'warning' : 'ok';
          if (element['change-time']) {
            element.status_date = formatDate(new Date(element['change-time']*1000));
          }
          content = promise_widget_template({
              element: element
            });
          gadget.element.querySelector(".content-details .ui-block-a")
            .innerHTML += content;

          amount = gadget.state.instance.state.warning +
            gadget.state.instance.state.error +
            gadget.state.instance.state.success;

          instance_content = instance_widget_template({
            title: gadget.state.instance.title,
            root_title: gadget.state.opml_outline.opml_title,
            status: gadget.state.instance.status,
            date: gadget.state.instance.date,
            errors: gadget.state.instance.state.error + "/" + amount,
            warning: gadget.state.instance.state.warning + "/" + amount,
            success: gadget.state.instance.state.success + "/" + amount,
            instance: gadget.state.instance._embedded.instance,
            instance_url: "#page=software_instance_view&key=" +
              gadget.state.instance.reference,
            hosting_url: "#page=hosting_subscription_view&key=" +
              gadget.state.opml.url,
            public_url: gadget.state.instance._links.public_url.href,
            private_url: pass_url
          });
          links_content = links_widget_template({
            public_url: gadget.state.instance._links.public_url.href,
            private_url: pass_url
          });
          gadget.element.querySelector(".content-details .ui-block-b  .promise-instance")
            .innerHTML += instance_content;
          /*gadget.element.querySelector(".content-details .ui-block-b .promise-links")
            .innerHTML += links_content;*/
          history_content = history_widget_template({history_list: []});
          gadget.element.querySelector(".content-details .ui-block-a")
                  .innerHTML += history_content;
        })
        .push(function () {
          return gadget.state.jio_gadget.createJio({
            type: "webhttp",
            url: gadget.state.promise.source_url.replace("jio_public", "public")
          });
        })
        .push(function () {
          return gadget.property_dict.render_deferred.resolve();
        });
        /*
          .push(function () {
            return gadget.property_dict.login_gadget.loginRedirect(
              global_state._links.private_url.href,
              options,
              global_state.title,
              global_state['hosting-title']);
          })
          .push(function (cred) {
            var jio_options,
              jio_key = "monitor_state.data",
              data_url = global_state._links.private_url.href + 'data/';

            jio_options = {
              type: "query",
              sub_storage: {
                type: "drivetojiomapping",
                sub_storage: {
                  type: "dav",
                  url: data_url,
                  basic_login: cred.hash
                }
              }
            };
            gadget.property_dict.jio_gadget.createJio(jio_options, false);
            return gadget.property_dict.jio_gadget.get(jio_key);
          })
          .push(function (monitor_state) {
            var data = {
                labels: [],
                datasets: [
                  {
                    label: "SUCCESS",
                    fillColor: "rgba(21, 246, 21, 0)",
                    strokeColor: "rgba(21, 246, 21,1)",
                    pointColor: "rgba(21, 246, 21,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(21, 246, 21,1)",
                    data: []
                  },
                  {
                    label: "ERROR",
                    fillColor: "rgba(255, 14, 44, 0)",
                    strokeColor: "rgba(255, 14, 44, 1)",
                    pointColor: "rgba(255, 14, 44, 1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(255, 14, 44, 1)",
                    data: []
                  },
                  {
                    label: "WARNING",
                    fillColor: "rgba(239, 196, 56,0)",
                    strokeColor: "rgba(239, 196, 56,1)",
                    pointColor: "rgba(239, 196, 56,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(239, 196, 56,1)",
                    data: []
                  }
                ]
              },
              i,
              tmp,
              start = 0;
              
            if (monitor_state.hasOwnProperty('data')) {
              if (monitor_state.data.length > 20) {
                start = monitor_state.data.length - 20;
              }
              for (i = start; i < monitor_state.data.length; i += 1) {
                tmp = monitor_state.data[i].split(',');
                data.labels.push(tmp[0]);
                data.datasets[0].data.push(tmp[1]);
                data.datasets[1].data.push(tmp[2]);
                data.datasets[2].data.push(tmp[3]);
              }
            }
            return gadget.property_dict.chart1.render({
              type: 'line',
              config: {
                bezierCurve: false,
                responsive: true
              },
              data: data
            });
          })
          .push(function () {
            var data = {
              labels: [global_state.date],
              datasets: [
                {
                  label: "SUCCESS",
                  fillColor: "rgba(21, 246, 21, 0.7)",
                  strokeColor: "rgba(21, 246, 21,1)",
                  pointColor: "rgba(21, 246, 21,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(21, 246, 21,1)",
                  data: [global_state.state.success],
                  name: "success"
                },
                {
                  label: "ERROR",
                  fillColor: "rgba(255, 14, 44, 0.7)",
                  strokeColor: "rgba(255, 14, 44, 1)",
                  pointColor: "rgba(255, 14, 44, 1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(255, 14, 44, 1)",
                  data: [global_state.state.error],
                  name: "error"
                },
                {
                  label: "WARNING",
                  fillColor: "rgba(239, 196, 56,0.7)",
                  strokeColor: "rgba(239, 196, 56,1)",
                  pointColor: "rgba(239, 196, 56,1)",
                  pointStrokeColor: "#fff",
                  pointHighlightFill: "#fff",
                  pointHighlightStroke: "rgba(239, 196, 56,1)",
                  data: [global_state.state.warning],
                  name: "warning"
                }
              ]
            };
            return gadget.property_dict.chart0.render({
              type: 'bar',
              config: {
                bezierCurve: false,
                responsive: true,
                barDatasetSpacing: 20
              },
              data: data
            });
          })*/
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    //.declareAcquiredMethod('loginRedirect', 'loginRedirect')
    .declareService(function () {
      var gadget = this,
        promise_list = [];

      promise_list.push(loopEventListener(
        gadget.element.querySelector('.loadbox'),
        'click',
        false,
        function (evt) {
          return new RSVP.Queue()
            .push(function () {
              var text = gadget.element.querySelector('.loadbox .loadwait a');
              $(".loadbox .signal").removeClass("ui-content-hidden");
              if (text) {
                text.textContent = "Loading...";
              }
            })
            .push(function () {
              var history_content;
    
              return gadget.state.jio_gadget.get(
                gadget.state.promise.source + ".history"
              )
              .push(undefined, function (error) {
                console.log(error);
                return undefined;
              })
              .push(function (status_history) {
                var i,
                  start_index = 0,
                  history_size,
                  history_list = [];

                $(".loadbox .signal").addClass("ui-content-hidden");
                if (status_history && status_history.hasOwnProperty('data')) {
                  if (history_size > 600) {
                    start_index = history_size - 600;
                  }
                  history_size = status_history.data.length;
                  for (i = start_index; i < history_size; i += 1) {
                    history_list.push(status_history.data[i]);
                  }
                  history_list.reverse();
                }
                history_content = load_history_template({
                  history_list: history_list
                });
                gadget.element.querySelector(".loadbox")
                      .innerHTML = history_content;
                return $('.loadbox table').table().table("refresh");
              });
            });
        }
      ));

      return RSVP.all(promise_list);
    });


}(window, rJS, Handlebars, RSVP, $));