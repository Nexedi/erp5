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
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareMethod("render", function (options) {
      var gadget = this,
        id = options.id,
        list_method_template;
      console.log(options);
      gadget.props.options = options;
      return gadget.jio_get(id)
        .push(function (result) {
          gadget.props.element.querySelector("a").setAttribute("href",id + "/");
          gadget.props.element.querySelector("h1").textContent = 
            result.short_title ? result.short_title : ""; 
          gadget.props.element.querySelector("p").textContent = 
            result.description ? result.description : ""; 
          return gadget.jio_getAttachment(id, "links");
        })
        .push(function (result) {
          return gadget.jio_getAttachment(id,
            // Should not be harcoded. You should look for section_content in list 
            result._links.action_object_view[3].href);
        })
        .push(function (result) {
          list_method_template = result._embedded._view.listbox.list_method_template;
          return gadget.jio_allDocs({
              query: '(portal_type:"Image" OR portal_type:"Web Illustration") AND strict_publication_section_relative_url:"publication_section/application/logo"',
              list_method_template: list_method_template,
              select_list: ['relative_url', 'reference']
            });
        })
        .push(function (result) {
          if (result.data.total_rows !== 0) {
            gadget.props.element.querySelector("img").setAttribute("src",
              result.data.rows[0].value.reference + "?format=png&display=thumbnail"
              )
          } else {
            // XXX Here we should have a fallback image
          }
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