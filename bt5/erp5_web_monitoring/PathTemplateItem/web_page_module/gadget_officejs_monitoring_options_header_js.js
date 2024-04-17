/*global document, window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getOptions", function (argument_list) {
      console.log("header getOptions...", argument_list);
      return {'a': 1};
    });

}(document, window, rJS, RSVP));