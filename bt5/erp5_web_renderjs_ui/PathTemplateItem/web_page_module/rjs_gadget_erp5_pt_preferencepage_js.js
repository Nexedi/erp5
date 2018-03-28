/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
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
          return gadget.jio_getAttachment(
            'portal_preferences',
            result._links.action_preferences.href
          );
        })
        .push(function (result) {
          return gadget.redirect({command: 'display', options: {jio_key: result.preference}});
        });
    });
}(window, rJS));
