/*jslint indent: 2 */
/*global window, rJS, PDFJS, webViewerLoad, Uint8Array, ArrayBuffer*/
(function (window, rJS, PDFJS, webViewerLoad) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })
    .declareMethod('render', function (options) {
      [].forEach.call(window.document.head.querySelectorAll("base"), function (el) {
        // XXX GadgetField adds <base> tag to fit to the parent page location, it's BAD to remove them.
        //     In the case of method-draw, all component are loaded dynamicaly through ajax requests in
        //     method-draw "folder". By setting a <base> tag, we change the url resolution behavior, and
        //     we break all dynamic links. So, deleting <base> is required.
        window.document.head.removeChild(el);
      });

      var raw = window.atob(options.value);
      var rawLength = raw.length;
      var array = new Uint8Array(new ArrayBuffer(rawLength));

      // Enable fullscreen Mod
      return this.allowFullScreen()
        .push(function () {
        // Hide open file button
        window.document.getElementById('openFile').hidden = true;

        for (var i = 0; i < rawLength; i++) {
          array[i] = raw.charCodeAt(i);
        }

        webViewerLoad(array);
      });
      //return {};
    })
    .declareService(function () {
      if (/(?:^\?|&)auto_focus=(true|1)(?:&|$)/.test(window.location.search)) {
        window.focus();  // should be done by the parent gadget?
      }
    })
    .declareMethod('getContent', function () {
      return "";
    })
    .declareAcquiredMethod("allowFullScreen", "allowFullScreen");

}(window, rJS, PDFJS, webViewerLoad));
