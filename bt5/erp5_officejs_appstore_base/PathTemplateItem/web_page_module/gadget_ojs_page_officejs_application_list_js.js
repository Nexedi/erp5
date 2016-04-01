/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa, SimpleQuery, ComplexQuery, Query */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        page_title: "OfficeJS Applications",
        panel_action: false
      })
        .push(function () {
          return gadget.jio_allDocs({
            query: 'portal_type:("Web Site") AND validation_state:"published"',
            select_list: ['uid']
          });
        })
        .push(function (result) {
          var i, i_len, query, uid_query_list = [];
          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {
            uid_query_list.push(
              new SimpleQuery({
                key: 'parent_uid',
                value: result.data.rows[i].value.uid
              })
            );
          }
          query = new ComplexQuery({
            operator: "AND",
            query_list: [
              new ComplexQuery({operator: "OR", query_list: uid_query_list}),
              new SimpleQuery({key: "portal_type", value: "Web Section"}),
              new SimpleQuery({key: "id", value: "latest"})
            ]
          });
          return gadget.jio_allDocs({
            query: Query.objectToSearchText(query)
          });
        })
        .push(function (result) {
          var list_element = gadget.props.element.querySelector("ul"),
            queue = new RSVP.Queue(),
            i, i_len;

          function addApplication(id) {
            queue.push(function () {
              var element = document.createElement("li");
              list_element.appendChild(element);
              return gadget.declareGadget(
                "gadget_officejs_application_presentation_element.html",
                {
                  element: element
                }
              );
            }).push(function (application_presentation_element) {
              return application_presentation_element.render({id: id});
            });
          }

          // XXX Should clean list prior to adding any element
          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {
            addApplication(result.data.rows[i].id);
          }
          return queue;
        })
        .push(function () {
          return gadget.props.deferred.resolve();
        });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return true;
        });
    });


}(window, rJS, RSVP, SimpleQuery, ComplexQuery, Query));