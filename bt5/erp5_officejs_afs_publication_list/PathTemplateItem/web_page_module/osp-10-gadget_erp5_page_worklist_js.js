/*global window, rJS, RSVP, Handlebars, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, URI) {
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
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.updateHeader({
        page_title: 'Worklist'
      })
        .push(function () {
          return gadget.jio_getAttachment(
            'portal_workflow',
            'links'
          );
        })
        .push(function (result) {
          return gadget.jio_getAttachment(
            // result.data.rows[0].id,
            'portal_workflow',
            result._links.action_worklist.href
          );
        })
        .push(function (links) {
          var action_list = links.worklist,
            query_string,
            promise_list = [],
            i;
          for (i = 0; i < action_list.length; i += 1) {

            query_string = new URI(action_list[i].href).query(true).query;

            promise_list.push(RSVP.all([
              gadget.getUrlFor({command: 'display', options: {
                jio_key: new URI(action_list[i].module).segment(2),
                extended_search: query_string,
                page: 'form',
                view: 'view'
              }}),
              // Remove the counter from the title
              action_list[i].name.replace(/ \(\d+\)$/, ''),
              action_list[i].count
            ]));

          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          var line_list = [],
            i;
          for (i = 0; i < result_list.length; i += 1) {
            line_list.push({
              link: result_list[i][0],
              title: result_list[i][1],
              count: result_list[i][2]
            });
          }
          return gadget.translateHtml(table_template({
            documentlist: line_list
          }));
        })

        .push(function (my_translated_html) {
          gadget.props.element.querySelector('.document_list').innerHTML =
            my_translated_html;
        });
    });

}(window, rJS, RSVP, Handlebars, URI));