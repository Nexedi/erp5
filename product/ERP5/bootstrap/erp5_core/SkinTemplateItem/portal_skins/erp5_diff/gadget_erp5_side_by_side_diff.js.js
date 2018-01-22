/*global rJS, RSVP, Diff2Html, window */
/*jslint nomen: true, indent: 2, maxerr: 3 */
/**
Side by side Diff is a gadget whcih we use to display diff between any 2 ERP5
objects in side by side view
**/
(function (rJS, RSVP, Diff2Html, window) {
  "use strict";

  rJS(window)

    .declareMethod('render', function (options) {
      this.element.innerHTML = Diff2Html.getPrettyHtml(options.value, {
          outputFormat: 'side-by-side',
          matching: 'lines'
        });
    });

}(rJS, RSVP, Diff2Html, window));
