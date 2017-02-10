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
      [].forEach.call(window.document.head.querySelectorAll("base"), function (el) {
        // XXX GadgetField adds <base> tag to fit to the parent page location, it's BAD to remove them.
        //     In the case of pdf.js, all component are loaded dynamicaly through ajax requests in
        //     pdf-js "folder". By setting a <base> tag, we change the url resolution behavior, and
        //     we break all dynamic links. So, deleting <base> is required.
        window.document.head.removeChild(el);
      });
      this.props.key = options.key;
      var raw = window.atob(options.value);
      var rawLength = raw.length;
      var array = new Uint8Array(new ArrayBuffer(rawLength));

      for (var i = 0; i < rawLength; i++) {
        array[i] = raw.charCodeAt(i);
      }

      webViewerLoad(array);

      // hide few buttons for now
      this.props.element.querySelector('#viewBookmark').hidden = true;
      this.props.element.querySelector('#documentProperties').hidden = true;
      this.props.element.querySelector('#documentProperties').hidden = true;
      
      return;
    })
    .declareMethod("getContent", function () {
      var form_data = {};
      var self = this;
      return new RSVP.Queue()
      .push(function () {
        if (PDFViewerApplication.pdfDocument) {
          return PDFViewerApplication.pdfDocument.getData();
        } else {
          return '';
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
