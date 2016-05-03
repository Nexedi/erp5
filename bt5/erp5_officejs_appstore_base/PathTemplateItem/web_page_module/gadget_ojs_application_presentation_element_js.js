/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa, ComplexQuery, Query */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  var gadget_klass = rJS(window);

  function getViewLink(gadget, id, action_id) {
    return gadget.jio_getAttachment(id, 'links')
      .push(function (result) {
        var i, i_len, links;
        links = result._links.action_object_view;
        if (links.constructor !== Array) {
          links = [links];
        }
        for (i = 0, i_len = links.length; i < i_len; i += 1) {
          if (links[i].name === action_id) {
            return links[i];
          }
        }
        return undefined;
      });
  }

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
      gadget.props.options = options;
      return gadget.jio_get(id)
        .push(function (result) {
          gadget.props.element.querySelector("h1").textContent =
            result.short_title || "";
          gadget.props.element.querySelector("p").textContent =
            result.description || "";
          return RSVP.all([
            getViewLink(gadget, id, "section_content"),
            getViewLink(gadget, id, "layout_configuration")
          ]);
        })
        .push(function (result) {
          // XX Should it raise if result is undefined? 
          return RSVP.all([
            gadget.jio_getAttachment(id, result[0].href),
            gadget.jio_getAttachment(id, result[1].href)
          ]);
        })
        .push(function (result) {
          list_method_template = result[0]._embedded._view.listbox.list_method_template;
          gadget.props.element.querySelector("a").setAttribute(
            "href",
            result[1]._embedded._view.my_configuration_resource_base_url.default
          );
          return gadget.jio_allDocs({
            query: '(portal_type:"Image" OR portal_type:"Web Illustration") AND strict_publication_section_relative_url:"publication_section/application/logo"',
            list_method_template: list_method_template,
            select_list: ['relative_url', 'reference']
          });
        })
        .push(function (result) {
          if (result.data.total_rows !== 0) {
            gadget.props.element.querySelector("img").setAttribute(
              "src",
              result.data.rows[0].value.reference + "?format=png&display=thumbnail"
            );
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


}(window, rJS, RSVP));