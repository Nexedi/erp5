/*global window, rJS, RSVP, jIO, DOMParser, Object, Intl */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, Object) {
  "use strict";

  rJS(window)

    .ready(function (gadget) {
      return gadget.getDeclaredGadget('export')
        .push(function (jio_gadget) {
          gadget.state_parameter_dict = {jio_storage: jio_gadget};
        });
    })

    .declareMethod('createJio', function (options) {
      return this.state_parameter_dict.jio_storage.createJio(options);
    })
    .declareMethod('allDocs', function (options) {
      return this.state_parameter_dict.jio_storage.allDocs(options);
    })
    .declareMethod('get', function (id) {
      return this.state_parameter_dict.jio_storage.get(id);
    });

}(window, rJS, RSVP, Object, Intl));