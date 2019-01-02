/*global window, document, rJS, RSVP,
    loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, document, RSVP) {
  "use strict";

  function addLine(gadget, app_name, edited_app_dict) {
    return new RSVP.Queue()
      .push(function () {
        return gadget.getUrlFor({page: "jio_crib_configurator", communication_gadget: edited_app_dict[app_name].communication_gadget, application_name: app_name});
      })
      .push(function (url) {
        var line = document.createElement("tr"),
            table = gadget.element.querySelector(".connect_list");
          line.innerHTML = '<td><a class="ui-link" href="' + url + '">' + app_name +
            '</a></td><td><a class="ui-link" href="' + url + '">' + edited_app_dict[app_name].communication_gadget +
            '</a></td><td><a class="ui-link" href="' + url + '">' + edited_app_dict[app_name].erp5_url + '</a></td>';
        table.appendChild(line);
        return;
      });
  }

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.getUrlFor({page: "jio_crib_configurator"})
        .push(function (url) {
          return gadget.updateHeader({
            title: "Application List",
            add_url: url
          });
        })
        .push(function () {
          return gadget.getSetting("edited_app_dict", {});
        })
        .push(function (edited_app_dict) {
          var app_name, promise_list = [];
          for (app_name in edited_app_dict) {
            promise_list.push(addLine(gadget, app_name, edited_app_dict));
          }
          return RSVP.all(promise_list);
        });
    })

}(window, rJS, document, RSVP));