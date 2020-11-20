/*jslint indent: 2, nomen: true */
/*global window, rJS, RSVP, PDFJS, configure, webViewerInitialized,
        PDFViewerApplication, FileReader, PasswordPrompt */
(function (window, rJS, RSVP, PDFJS, configure, webViewerInitialized, PDFViewerApplication, PasswordPrompt) {
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
      var gadget = this;
      gadget.props.key = options.key;
      configure(PDFJS);
      PDFJS.locale = options.language;
      if (options.password) {
        PasswordPrompt._original_open = PasswordPrompt.open;
        var retries = 0;
        PasswordPrompt.open = function () {
          if (retries) {
            return this._original_open()
          }
          retries++;
          return this.updatePassword(options.password);
        }
      }
      return PDFViewerApplication.initialize().then(function() {
        webViewerInitialized(options.value);
        // hide some buttons that do not make sense for us 
        gadget.props.element.querySelector('#viewBookmark').hidden = true;
        gadget.props.element.querySelector('#documentProperties').hidden = true;
        gadget.props.element.querySelector('#documentProperties').hidden = true;
        gadget.props.element.querySelector('#download').hidden = true;
      })
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
}(window, rJS, RSVP, PDFJS, configure, webViewerInitialized, PDFViewerApplication, PasswordPrompt));
