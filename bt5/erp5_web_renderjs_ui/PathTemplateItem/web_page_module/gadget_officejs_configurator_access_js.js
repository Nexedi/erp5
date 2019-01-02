/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML,
    table_template = Handlebars.compile(source);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (storage_name) {
      var gadget = this;
      return gadget.getSetting("jio_storage_name", undefined)
        .push(function (name) {
          if (name === storage_name) {
            return RSVP.all([
              gadget.getUrlFor({command: "display"}),
              gadget.getUrlFor(
                {command: "display", options: {page: "ojs_sync", auto_repair: true}}
              ),
              gadget.getSetting("jio_storage_name", false)
            ]);
          }
          return [];
        })
        .push(function (result) {
          if (result[2]) {
            return gadget.element.querySelector('.document_list').innerHTML =
              table_template({document_list_href: result[0], sync_href: result[1]});
          }
        });
    });

}(window, rJS, RSVP, Handlebars, URI));