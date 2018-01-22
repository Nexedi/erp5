/*global rJS, jIO, RSVP, window */
/*jslint nomen: true, indent: 2, maxerr: 3 */
/**
Side by Side Diff is a gadget whcih we use to display diff between any 2 ERP5
objects in side by side view
**/
(function (rJS, jIO, RSVP, window) {
  "use strict";
  var gk = rJS(window);

  rJS(window)

    .declareMethod('render', function (options) {
      var patch = options.value;
      var html = Diff2Html.getPrettyHtml(patch, {
        outputFormat: 'side-by-side',
        matching: 'lines'
      });
      this.element.innerHTML = html;
    });

}(rJS, jIO, RSVP, window));
