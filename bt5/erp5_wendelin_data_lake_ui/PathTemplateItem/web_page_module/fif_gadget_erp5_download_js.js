/*global window, rJS, console, document */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, console, document) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareService(function () {
      var gadget = this,
        download_deb_element = document.querySelector("#deb_link"),
        jio_key = 'document_module/ebulk-1.1.9.deb';
      return gadget.jio_get(jio_key)
        .push(function (jio_document) {
          download_deb_element.download = jio_document.short_title;
          download_deb_element.href = window.location.origin + "/" + jio_key + "/getData";
        }, function (error) {
          console.log("Latest .deb ebulk package document not available:", error);
        });
    });
}(window, rJS, console, document));