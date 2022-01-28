/*global window, rJS, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, URI) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.jio_getAttachment(
        'portal_preferences',
        'links'
      )
        .push(function (result) {
          var jio_key;
          if (result._links.active_preference === undefined) {
            jio_key = 'portal_preferences';
          } else {
            jio_key = (new URI(result._links.active_preference
                                     .href)).segment(2);
          }
          return gadget.redirect({command: 'display_with_history',
                                  options: {jio_key: jio_key}});
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });
}(window, rJS, URI));
