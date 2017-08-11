/*global window, rJS, Handlebars, Rusha */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, Handlebars, Rusha) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    hosting_widget_template = Handlebars.compile(
      templater.getElementById("template-hostings-list").innerHTML
    ),
    rusha = new Rusha();

  function generateHash(str) {
    return rusha.digestFromString(str);
  }


  function getHostingStatus(gadget, id) {
    return gadget.jio_allDocs({
        query: '(portal_type:"opml-outline") AND (parent_id:"' + id + '")'
    })
      .push(function (ouline_list) {
        var j,
          promise_list = [];
        for (j = 0; j < ouline_list.data.total_rows; j += 1) {
          // fetch all instance info to build hosting status
          promise_list.push(
            gadget.jio_allDocs({
              select_list: ["status", "date"],
              query: '(portal_type:"global") AND (parent_id:"' +
                ouline_list.data.rows[j].id + '")'
            })
          );
        }
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        var i,
          j,
          status = "OK",
          warning = "",
          date = 'Not Synchronized';

        for (i = 0; i < result_list.length; i += 1) {
          for (j = 0; j < result_list[i].data.total_rows; j += 1) {
            if (warning !== "" &&
                result_list[i].data.rows[j].value.status === "WARNING") {
              warning = "WARNING";
            }
            if (status !== "ERROR" && status !== "WARNING" &&
                result_list[i].data.rows[j].value.status === "ERROR") {
              // continue and only change the status if we found Warning === state inconsistent
              status = result_list[i].data.rows[j].value.status;
              date = result_list[i].data.rows[j].value.date;
            } else {
              date = result_list[i].data.rows[j].value.date;
            }
          }
        }
        if (date === 'Not Synchronized') {
          status = "WARNING";
        }
        return {
          id: id,
          status: warning || status,
          amount: result_list.length,
          date: date
        };
      });
  }

  gadget_klass
    .setState({
      render_deferred: "",
      opml_dict: ""
    })
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.changeState({"render_deferred": RSVP.defer()});
    })
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("renderApplication", "renderApplication")
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareMethod("render", function (options) {
      var gadget = this;

      gadget.props.options = options;
      return gadget.updateHeader({
          title: 'Monitoring Hosting Subscriptions'
        })
        .push(function () {
          return gadget.jio_allDocs({
            select_list: ["basic_login", "url", "title"],
            query: '(portal_type:"opml") AND (active:true)',
            sort_on: [["title", "descending"]]
          });
        })
        .push(function (opml_result) {
          var i,
            opml_dict = {},
            promise_list = [],
            id;
          for (i = 0; i < opml_result.data.total_rows; i += 1) {
            id = generateHash(opml_result.data.rows[i].value.url);
            opml_dict[id] = {
              url: opml_result.data.rows[i].value.url,
              basic_login: opml_result.data.rows[i].value.basic_login,
              status: "WARNING",
              date: 'Not Synchronized',
              title: opml_result.data.rows[i].value.title,
              amount: 0
            };
            promise_list.push(getHostingStatus(gadget, id));
          }
          return new RSVP.Queue()
            .push(function () {
              return RSVP.all(promise_list);
            })
            .push(function (status_list) {
              var i;
              for (i = 0; i < status_list.length; i += 1) {
                opml_dict[status_list[i].id].status = status_list[i].status;
                opml_dict[status_list[i].id].date = status_list[i].date;
                opml_dict[status_list[i].id].amount = status_list[i].amount;
              }
              return gadget.changeState({opml_dict: opml_dict});
            });
        })
        .push(function () {
          var content,
            key,
            hosting_list = [],
            cred_list;

          for (key in gadget.state.opml_dict) {
            if (gadget.state.opml_dict.hasOwnProperty(key)) {
              if (gadget.state.opml_dict[key].date === 'Not Synchronized') {
                cred_list = atob(gadget.state.opml_dict[key].basic_login).split(':');
                gadget.state.opml_dict[key].href = '#page=settings_configurator' +
                  '&tab=add&url=' + gadget.state.opml_dict[key].url +
                  '&username=' + cred_list[0] + '&password=' + cred_list[1];
              } else {
                gadget.state.opml_dict[key].href = "#page=hosting_subscription_view&key=" +
                  gadget.state.opml_dict[key].url;
              }
            }
            hosting_list.push(gadget.state.opml_dict[key]);
          }
          content = hosting_widget_template({
            hosting_list: hosting_list
          });
          gadget.element.querySelector('.hosting-list table tbody')
            .innerHTML = content;

          return gadget.state.render_deferred.resolve();
        });
    })


    .declareService(function () {
      var gadget = this,
        current_sync_date;

      return new RSVP.Queue()
        .push(function () {
          return gadget.state.render_deferred.promise;
        })
        .push(function () {
          return gadget.getSetting('latest_sync_time');
        })
        .push(function (sync_time) {
          current_sync_date = sync_time;
          return gadget.getSetting('status_list_refresh_id');
        })
        .push(function (timer_id) {
          var new_timer_id;
          if (timer_id) {
            clearInterval(timer_id);
          }
          new_timer_id = setInterval(function() {
            var hash = window.location.toString().split('#')[1],
              scroll_position,
              doc = document.documentElement;
            if (hash.indexOf('page=hosting_subscription_list') >= 0) {
              return gadget.getSetting('latest_sync_time')
                .push(function (sync_time) {
                  if (sync_time > current_sync_date) {
                    scroll_position = (window.pageYOffset || doc.scrollTop)  - (doc.clientTop || 0);
                    current_sync_date = sync_time;
                    return gadget.renderApplication({args: gadget.props.options})
                      .push(function () {
                        $(document).scrollTop(scroll_position);
                      });
                  }
                });
            }
          }, 60000);
          return gadget.setSetting('status_list_refresh_id', new_timer_id);
        });

    });

}(window, rJS, Handlebars, Rusha));