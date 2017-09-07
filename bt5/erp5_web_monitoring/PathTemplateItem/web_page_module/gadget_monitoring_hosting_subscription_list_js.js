/*global window, rJS, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    hosting_widget_template = Handlebars.compile(
      templater.getElementById("template-hostings-list").innerHTML
    );

  function getHostingData(gadget) {
    // optimized way to fetch hosting subscription list
    var hosting_dict = {},
      instance_dict = {};
    return gadget.jio_allDocs({
          select_list: ["basic_login", "url", "title"],
          query: '(portal_type:"opml") AND (active:true)',
          sort_on: [["title", "descending"]]
        })
      .push(function (result) {
        var i;
        for (i = 0; i < result.data.total_rows; i += 1) {
          hosting_dict[result.data.rows[i].id] = {
            url: result.data.rows[i].value.url,
              basic_login: result.data.rows[i].value.basic_login,
              status: "WARNING",
              date: 'Not Synchronized',
              title: result.data.rows[i].value.title,
              amount: 0
          };
        }
        return gadget.jio_allDocs({
          query: '(portal_type:"opml-outline")',
          select_list: [
            "parent_url"
          ]
        });
      })
      .push(function (result) {
        var i;
        for (i = 0; i <result.data.total_rows; i += 1) {
          if (hosting_dict.hasOwnProperty(result.data.rows[i].value.parent_url)) {
            instance_dict[result.data.rows[i].id] = {
              parent_id: result.data.rows[i].value.parent_url
            };
          }
        }
        return gadget.jio_allDocs({
          query: '(portal_type:"global")',
          select_list: [
            "status",
            "parent_id",
            "date"
          ]
        });
      })
      .push(function (result) {
        var i;
        for (i = 0; i < result.data.total_rows; i += 1) {
          if (instance_dict.hasOwnProperty(result.data.rows[i].value.parent_id)) {
            instance_dict[result.data.rows[i].value.parent_id].date =
              result.data.rows[i].value.date;
            instance_dict[result.data.rows[i].value.parent_id].status =
              result.data.rows[i].value.status;
          }
        }
      })
      .push(function () {
        //build hosting subscription data
        var key,
          item;
        for (key in instance_dict) {
          if (instance_dict.hasOwnProperty(key)) {
            item = hosting_dict[instance_dict[key].parent_id];
            item.amount += 1;
            if (item.status !== "ERROR") {
              item.status = instance_dict[key].status;
            }
            item.date = instance_dict[key].date;
          }
        }
        return gadget.changeState({opml_dict: hosting_dict});
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
          return getHostingData(gadget);
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

}(window, rJS, Handlebars));