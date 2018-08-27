/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareMethod("method1", function (param1, param2) {
      return;
    })
    .declareMethod("method2", function (param1) {
      return;
    })
    .declareMethod("method3", function () {
      return;
    })
    .declareMethod("method4", function () {
      return;
    });

}(window, rJS));