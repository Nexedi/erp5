/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('triggerMaximize', 'triggerMaximize')

    .onEvent('click', function (event) {
      if (event.target.tagName === "BUTTON") {
        return this.callMaximize(true);
      }
    })
    .declareJob('callMaximize', function () {
      return this.triggerMaximize(true);
    });

}(window, rJS));