/*global document, window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 90 */
(function (document, window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this, id,
        types = '("Text", "File", "PDF", "Drawing", ' +
          '"Presentation", "Spreadsheet")',
        states = '("shared", "published", "released", ' +
          '"shared_alive", "published_alive", "released_alive")',
        query = 'portal_type:' + types +
          'AND reference:"' + options.reference +
          '" AND validation_state:' + states,
        redirect_dict = {
          'command': 'display',
          'options': {
            'history': options.history
          }
        };
      return gadget.jio_allDocs({
        query: query,
        limit: 1
      })
        .push(function (result_list) {
          if (result_list.data.rows[0]) {
            redirect_dict.options.jio_key = result_list.data.rows[0].id;
          }
          //TODO else: redirect to previous and show not found error
          return gadget.redirect(redirect_dict);
        });
    });

}(document, window, rJS));