/*global window, rJS, RSVP, Handlebars, jIO, location, console */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, jIO, Handlebars, RSVP, window) {
  "use strict";
  var gk = rJS(window);


  rJS(window)

    .declareMethod('render', function (options) {
      var patch = options.value;
      this.element.innerHTML = Diff2Html.getPrettyHtml(patch, {
                                                  outputFormat: 'side-by-side',
                                                  matching: 'lines',})
    });

}(rJS, jIO, Handlebars, RSVP, window));
