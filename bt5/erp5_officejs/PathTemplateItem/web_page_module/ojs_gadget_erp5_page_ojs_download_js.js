/*global window, rJS, Blob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Blob) {
  "use strict";
  function downloadFromTextContent(gadget, text_content, title) {
    var element = gadget.element,
      a = window.document.createElement("a"),
      url = window.URL.createObjectURL(new Blob([text_content], {type: 'text/plain'})),
      name_list = [title, "txt"];
    element.appendChild(a);
    a.style = "display: none";
    a.href = url;
    a.download = name_list.join('.');
    a.click();
    element.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.jio_get(options.jio_key)
        .push(function (doc) {
          return downloadFromTextContent(gadget, doc.text_content, doc.title);
        })
        .push(function () {
          return gadget.redirect({
            'command': 'display',
            'options': {
              'jio_key': options.jio_key
            }
          });
        });
    });
}(window, rJS, Blob));