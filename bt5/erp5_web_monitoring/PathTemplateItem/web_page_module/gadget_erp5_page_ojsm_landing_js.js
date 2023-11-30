/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("landing-template")
                         .innerHTML,
    landing_template = Handlebars.compile(source);

  function searchItem(gadget, search_query) {
    return gadget.redirect({"command": "display", options: {}});
  }

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.changeState({
            original_query: options.original_query,
            query: options.query
          });
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return searchItem(gadget, gadget.state.query);
        })
        .push(function (search_result) {
          if (search_result === undefined && gadget.state.query) {
            gadget.element.querySelector('.search-result')
              .innerHTML = landing_template({});
          }
        });
    });

}(window, rJS, RSVP, Handlebars));