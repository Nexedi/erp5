/*global window, rJS, RSVP, jIO, document, URL */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO, document, URL) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_get", "jio_get")
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
      var gadget = this;

      return gadget.notifySubmitting()
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment(gadget.state.jio_key, 'data?docx'),
            gadget.jio_get(gadget.state.jio_key)
          ]);
        })
        .push(function (result) {
          var a = document.createElement('a'),
             url = URL.createObjectURL(result[0]);
          a.href = url;
          a.download = result[1].filename.split('docy')[0] +  'docx';
          gadget.element.appendChild(a);
          a.click();
          gadget.element.removeChild(a);
          URL.revokeObjectURL(url);
          return gadget.notifySubmitted();
        })
        .push(function () {
          return gadget.redirect({
            command: "display",
            options: {jio_key: gadget.state.jio_key}
          });
        });
    });
}(window, rJS, RSVP, jIO, document, URL));