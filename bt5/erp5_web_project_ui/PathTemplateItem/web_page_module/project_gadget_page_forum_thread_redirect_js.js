/*global window, rJS, SimpleQuery, ComplexQuery, Query */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 90 */
(function (window, rJS, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  // WIP: no structured API seeds an arbitrary back-target, so the forum-as-back
  // navigation has to be hand-built as a push_history_stored_state command URL.
  function buildThreadCommandUrl(forum_jio_key, thread_jio_key) {
    return '#!push_history_stored_state' +
      '?p.jio_key=' + encodeURIComponent(forum_jio_key) + '&p.page=form&p.view=view' +
      '&n.jio_key=' + encodeURIComponent(thread_jio_key) + '&n.page=form&n.view=view';
  }

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
      var gadget = this,
        forum_jio_key = options.jio_key,
        query = Query.objectToSearchText(new ComplexQuery({
          operator: "AND",
          type: "complex",
          query_list: [
            new SimpleQuery({
              key: "portal_type",
              operator: "",
              type: "simple",
              value: "Discussion Thread"
            }),
            new SimpleQuery({
              key: "reference",
              operator: "=",
              type: "simple",
              value: options.old_thread
            })
          ]
        }));

      return gadget.jio_allDocs({
        query: query,
        limit: 1
      })
        .push(function (result_list) {
          var row = result_list.data.rows[0];
          if (row) {
            return gadget.redirect({
              command: 'raw',
              options: {url: buildThreadCommandUrl(forum_jio_key, row.id)}
            });
          }
          // Unresolved reference: land on the forum.
          return gadget.redirect({
            command: 'display',
            options: {jio_key: forum_jio_key, page: 'form', view: 'view'}
          });
        });
    });

}(window, rJS, SimpleQuery, ComplexQuery, Query));
