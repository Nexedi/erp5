/*global window, rJS */
/*jslint nomen: true, indent:2*/
// Provides perspective worker
(function (window, rJS) {
  "use strict";
  rJS(window)
    .declareMethod("getTable", function (data) {
      return window.Worker.table(data);
    });

}(window, rJS));

