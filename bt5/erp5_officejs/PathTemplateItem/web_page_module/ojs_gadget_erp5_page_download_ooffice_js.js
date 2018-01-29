/*global window, rJS, RSVP, jIO, document, URL */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO, document, URL) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      return this.changeState({
        jio_key: options.jio_key
      });
    })
    .onStateChange(function () {
      var gadget = this,
        doc,
        jio_key,
        data,
        conversion_gadget,
        destination_mime_type = 'docx',
        source_mime_type = 'docy';

      return gadget.notifySubmitting()
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment(gadget.state.jio_key, 'data'),
            gadget.jio_get(gadget.state.jio_key),
            gadget.getDeclaredGadget('conversion')
          ]);
        })
        .push(function (result) {
          doc = result[1];
          conversion_gadget = result[2];
          return jIO.util.readBlobAsDataURL(result[0]);
        })
        .push(function (data_url) {
          return conversion_gadget.convert(data_url.target.result.split('base64,')[1], source_mime_type, destination_mime_type);
        })
        .push(function (data) {
          return conversion_gadget.b64toBlob(data);
        })
        .push(function (blob) {
          var a = document.createElement('a'),
             url = URL.createObjectURL(blob);
          a.href = url;
          a.download = doc.filename.split(source_mime_type)[0] + destination_mime_type;
          gadget.element.appendChild(a);
          a.click();
          gadget.element.removeChild(a);
          URL.revokeObjectURL(url);
          return gadget.notifySubmitted();
        })
        .push(function () {
          return gadget.redirect({command: "display", options: {jio_key: gadget.state.jio_key}});
        });
    });
}(window, rJS, RSVP, jIO, document, URL));