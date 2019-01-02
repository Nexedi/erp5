/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })

    .declareMethod("method1", function (param1, param2) {
      return;
    })

    //method2 is missing the declaration.

    .declareMethod("method3", function () {
      return;
    })
    .declareMethod("randommethod1", function (param1, param2, param3) {
      return;
    });

}(window, rJS));