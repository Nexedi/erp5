/*global window, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('triggerMaximize', 'triggerMaximize')

    .onEvent('click', function () {
      return this.triggerMaximize(true, this.defer.promise);
    })
    .declareService(function () {
      this.defer = RSVP.defer();
      return this.defer.promise;
    });

}(window, rJS, RSVP));