/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
        this.options = options;
        var script = document.createElement('script');
        script.setAttribute('id', 'jsmd');
        script.setAttribute('type', 'text/jsmd');
        script.innerHTML = options.value;
        document.body.appendChild(script);

        var iodide = document.createElement("script");
        iodide.src = "iodide_master.js";
        document.body.appendChild(iodide);

    })
    .declareMethod("getContent", function () {
        var dict = {};
        dict[this.options.key] = localStorage.getItem('AUTOSAVE: untitled');
        return dict;
    });
}(window, rJS, RSVP));