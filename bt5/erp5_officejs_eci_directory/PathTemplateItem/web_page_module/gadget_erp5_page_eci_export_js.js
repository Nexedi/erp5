/*globals window, RSVP, rJS, JSON, encodeURIComponent*/
/*jslint indent: 2, nomen: true, maxlen: 80*/

(function (window, RSVP, rJS, JSON, encodeURIComponent) {
  "use strict";
  rJS(window)
    .ready(function (gadget) {
      gadget.state_parameter_dict = {};
      //var api_key = window.prompt("Enter OpenHub API-Key or click 'Cancel'");
      var api_key = "";

      return gadget.getDeclaredGadget('export')
        .push(function (jio_gadget) {
          gadget.state_parameter_dict.jio_storage = jio_gadget;
          return gadget.state_parameter_dict.jio_storage.createJio({
            type: "export_storage",
            api_key: api_key
          });
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .declareMethod("render", function () {
      var gadget = this;
      var jio = gadget.state_parameter_dict.jio_storage;
      var dump = {};
      return new RSVP.Queue()
        .push(function () {
          gadget.updateHeader({
            page_title: 'Download'
          });
        })
        .push(function () {
          return jio.allDocs({});
        })
        .push(function (result_list) {
          var queue = new RSVP.Queue();
          var result_array = result_list.data.rows;
          var process_list = [];

          // process in chunks of 40 requests to not overwhelm OpenHub API
          while (result_array.length) {
            process_list.push(result_array.splice(0, 40));
          }
          process_list.map(function (process_array) {
            queue.push(function () {
              return RSVP.all(process_array.map(function (obj) {
                return new RSVP.Queue()
                  .push(function () {
                    return jio.get(obj.id);
                  })
                  .push(function (result) {
                    obj.value = result;
                    dump[obj.id] = result;
                  });
              }));
            });
          });
          return queue;
        })
        .push(function () {
          var str = "data:text/json;charset=utf-8," + encodeURIComponent(
            JSON.stringify(dump)
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
