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
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this,
        header_dict = {
          page_title: 'Worklist',
          page_icon: 'tasks'
        };

      return gadget.getUrlFor({command: 'display'})
        .push(function (url) {
          header_dict.front_url = url;
          return gadget.updateHeader(header_dict);
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
            display_options,
            i;
          for (i = 0; i < action_list.length; i += 1) {
            query_string = new URI(action_list[i].href).query(true).query;
            display_options = {extended_search: query_string};

            if (action_list[i].hasOwnProperty('module')) {
              display_options = {
                jio_key: new URI(action_list[i].module).segment(2),
                extended_search: query_string,
                page: 'form',
                view: 'view'
              };
            } else {
              display_options = {
                extended_search: query_string,
                page: 'search'
              };
            }
            promise_list.push(RSVP.all([
              gadget.getUrlFor({command: 'display_stored_state', options: display_options}),
              // Remove the counter from the title
              action_list[i].name,
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
            document_list: line_list
          }));
        })
        .push(function (translated_html) {
          gadget.element.querySelector('.document_list').innerHTML = translated_html;
        });
    });

}(window, rJS, RSVP, Handlebars, URI));