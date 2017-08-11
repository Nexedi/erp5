/*global window, rJS, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
    })
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareMethod("render", function (options) {
      var gadget = this,
        current_display;
      return gadget.jio_allDocs({query: 'portal_type:"opml"', limit: [0, 1]})
      .push(function (opml_result) {
        if (opml_result.data.total_rows === 0) {
          return gadget.redirect({
            page: 'import_export'
          });
        }
        return gadget.redirect({
          page: 'status_list'
        });
      });
    });

}(window, rJS));