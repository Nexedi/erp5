/*global window, rJS, RSVP, Handlebars, URI */
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
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;
      new RSVP.Queue().push(function () {
        return RSVP.all([
          gadget.getUrlFor({command: 'display', options: {page: "ojs_smart_assistant_document_list", extended_search: 'validation_state: "draft"'}}),
          gadget.getUrlFor({command: 'display', options: {page: "ojs_smart_assistant_document_list", extended_search: 'validation_state: "processing"'}}),
          gadget.jio_allDocs({"query": 'portal_type: ("Smart Assistant File" OR "Smart Assistant Image" OR "Smart Assistant Text" OR "Smart Assistant Sound") AND validation_state: "draft"'}),
          gadget.jio_allDocs({"query": 'portal_type: ("Smart Assistant File" OR "Smart Assistant Image" OR "Smart Assistant Text" OR "Smart Assistant Sound") AND validation_state: "processing"'})
        ]);
      })
        .push(function (result) {
          var line_list = [];
          line_list.push({
            link: result[0],
            title: "Smart Assistant Records to Start Processing",
            count: result[2].data.total_rows
          });
          line_list.push({
            link: result[1],
            title: "Smart Assistant Records to Finish Processing",
            count: result[3].data.total_rows
          });
          gadget.element.querySelector('.document_list').innerHTML = table_template({
            document_list: line_list
          });
        });
    });
}(window, rJS, RSVP, Handlebars));