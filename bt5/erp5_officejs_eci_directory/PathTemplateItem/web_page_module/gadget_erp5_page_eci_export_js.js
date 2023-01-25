/*globals window, RSVP, rJS, JSON, encodeURIComponent*/
/*jslint indent: 2, nomen: true, maxlen: 80*/

(function (window, RSVP, rJS, JSON, encodeURIComponent) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_get", "jio_get")

    .declareMethod("render", function () {
      var gadget = this;
      var dump = {};
      return gadget.updateHeader({
          page_title: 'Download'
        })
        .push(function () {
          return gadget.jio_allDocs();
        })
        .push(function (data) {
          var process_list = [],
            promise_list;
          promise_list = data.data.rows.filter(function (el) {
            return el.id.endsWith('.json');
          }).map(function (el) {
            return gadget.jio_get(el.id)
              .push(function (result) {
              dump[el.id] = result;
            });
          });
          return RSVP.all(promise_list);
        })
        .push(function () {
          var str = "data:text/json;charset=utf-8," + encodeURIComponent(
            JSON.stringify(dump, null, 2)
          );
          var download_button = window.document.createElement("a");
          download_button.setAttribute("href", str);
          download_button.setAttribute("download", "eci.json");
          download_button.classList.add("ui-hidden-accessible");
          window.document.body.appendChild(download_button);
          download_button.click();
          download_button.remove();
        });
    });
}(window, RSVP, rJS, JSON, encodeURIComponent));
