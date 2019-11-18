/*global window, rJS, SimpleQuery, ComplexQuery, Query */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 90 */
(function (window, rJS, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  function createMultipleSimpleOrQuery(key, value_list) {
    var i,
      search_query,
      query_list = [];
    for (i = 0; i < value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        operator: "",
        type: "simple",
        value: value_list[i]
      }));
    }
    search_query = new ComplexQuery({
      operator: "OR",
      query_list: query_list,
      type: "complex"
    });
    return Query.objectToSearchText(search_query);
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        type_list = ["Text", "File", "PDF", "Drawing",
          "Presentation", "Spreadsheet"],
        state_list = ["shared", "published", "released", "shared_alive",
          "published_alive", "released_alive"],
        portal_type_query = createMultipleSimpleOrQuery('portal_type', type_list),
        state_query = createMultipleSimpleOrQuery('validation_state', state_list),
        reference_query = new SimpleQuery({
          key: "reference",
          operator: "=",
          type: "simple",
          value: options.reference
        }),
        query = new ComplexQuery({
          operator: "AND",
          query_list: [portal_type_query, state_query, reference_query],
          type: "complex"
        });
      query = Query.objectToSearchText(query);
      return gadget.jio_allDocs({
        query: query,
        limit: 1
      })
        .push(function (result_list) {
          if (result_list.data.rows[0]) {
            return gadget.redirect({
              'command': 'display',
              'options': {
                'jio_key': result_list.data.rows[0].id,
                'history': options.history
              }
            });
          }
          return gadget.redirect({command: 'history_previous', options: {}});
        });
    });

}(window, rJS, SimpleQuery, ComplexQuery, Query));