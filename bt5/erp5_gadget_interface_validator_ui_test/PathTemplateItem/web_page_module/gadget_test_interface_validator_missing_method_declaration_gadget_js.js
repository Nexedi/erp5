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

// missing declaration of method2 and method3.
/*
    .declareMethod("method2", function (param1) {
      return;
    })

    .declareMethod("method3", function () {
      return;
    })
*/
    .declareMethod("randommethod1", function (param1, param2, param3) {
      return;
    });

}(window, rJS));