/*jslint indent: 2, nomen: true */
/*global window, rJS, RSVP, PDFJS, webViewerLoad, Uint8Array,
        ArrayBuffer, PDFViewerApplication, FileReader */
(function (window, rJS, RSVP, PDFJS, webViewerLoad) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.props.element = element;
        });
    })
    .declareMethod("render", function (options) {
      this.props.key = options.key;
      webViewerLoad(options.value);

      // hide few buttons for now
      this.props.element.querySelector('#viewBookmark').hidden = true;
      this.props.element.querySelector('#documentProperties').hidden = true;
      this.props.element.querySelector('#documentProperties').hidden = true;
      this.props.element.querySelector('#download').hidden = true;
      
      return;
    })
    .declareMethod("getContent", function () {
      var form_data = {};
      var self = this;
      return new RSVP.Queue()
      .push(function () {
        if (PDFViewerApplication.pdfDocument) {
          return PDFViewerApplication.pdfDocument.getData();
        }
      })
      .push(function (data) {
        var blob = PDFJS.createBlob(data, "application/pdf");
        var filereader = new FileReader();
        return new RSVP.Promise(function (resolve, reject, notify) {
          filereader.addEventListener("load", resolve);
          filereader.addEventListener("error", reject);
          filereader.addEventListener("progress", notify);
          filereader.readAsDataURL(blob);
        }, function () {
          filereader.abort();
        });
      })
      .push(function (evt) {
        form_data[self.props.key] = evt.target.result;
        return form_data;
      });
    });
}(window, rJS, RSVP, PDFJS, webViewerLoad, PDFViewerApplication));
