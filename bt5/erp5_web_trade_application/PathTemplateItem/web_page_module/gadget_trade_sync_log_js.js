/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-sync-log-template")
                              .innerHTML,
    template = Handlebars.compile(source);


  gadget_klass
    .ready(function (g) {
      g.props = {};
      g.options = null;
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("get", "jio_get")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      return new RSVP.Queue()
        .push(function (result_list) {
          return template({});
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          return gadget.updateHeader({
            title: "Sync Log"
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type: "Sync Log"',
            select_list: ["time", "result"],
            sort_on: [["time", "descending"]],
            limit: [0, 1234567890]
          });
        })
        .push(function (result) {
          var array = new Array();
          var i;
          var success = 0;
          for (i = 0; i < result.data.total_rows; i += 1) {
            array.push(result.data.rows[i].value.time + " " + result.data.rows[i].value.result);
            if (result.data.rows[i].value.result == 1){
              success++;
            }
          }
          gadget.props.element.querySelector('[name="log"]').innerHTML += array.join("\n");
          gadget.props.element.querySelector('[name="sync_success_ratio"]').value = String(Math.round(success / result.data.total_rows * 100)) + '%';
        })
    })

}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
