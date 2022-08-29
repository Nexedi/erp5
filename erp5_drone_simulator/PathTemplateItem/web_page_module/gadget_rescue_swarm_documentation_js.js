/*global window, rJS*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')
    .declareMethod('render', function () {
      var gadget = this;
      return gadget.getUrlFor({'command': 'history_previous'})
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "Rescue Swarm Documentation",
            selection_url: url
          });
        });
    });

}(window, rJS));