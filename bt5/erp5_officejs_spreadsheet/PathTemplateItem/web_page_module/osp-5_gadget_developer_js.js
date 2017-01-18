/*global window, rJS, document */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";
  
  rJS(window)

    .ready(function (gadget) {
      return gadget.getDeclaredGadget("develop_storage")
        .push(function (develop_storage) {
          gadget.app_url = window.location.origin + window.location.pathname.replace("dev/","");
          gadget.develop_storage = develop_storage;
          return gadget.develop_storage.createJio({
            type: "indexeddb",
            database: "officejs_code"
          });
        });
    })
          
    .declareAcquiredMethod("setSetting", "setSetting")

    .declareMethod("start", function () {
      var gadget = this;
      window.navigator.serviceWorker.addEventListener("message", function (event) {
        var id;
        if (event.data.relative_url) {
          id = gadget.app_url + (event.data.relative_url === "/" ? '' : event.data.relative_url);
          return gadget.develop_storage.get(id)
            .push(function (doc) {
              console.log("dev doc:", doc.url_string);
              event.ports[0].postMessage({"data":doc});
          })
            .push(undefined, function (error) {
              console.log(error, id);
          });
        }
      });
      return gadget.setSetting("dev_mode", true);
    });

}(window, rJS));