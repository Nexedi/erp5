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
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this,
        action_list;

      // Fetch worklist data
      return gadget.jio_getAttachment(
        'portal_workflow',
        'links'
      )
        .push(function (result) {
          return gadget.jio_getAttachment(
            // result.data.rows[0].id,
            'portal_workflow',
            result._links.action_worklist.href
          );
        })

        // Calculate all URLs
        .push(function (links) {
          var query_string,
            url_for_parameter_list = [
              // Back URL
              {command: 'display'},
              // Change language URL
              {command: 'display', options: {page: 'language'}}
            ],
            display_options,
            i;
          action_list = links.worklist;
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
            url_for_parameter_list.push(
              {command: 'display_stored_state', options: display_options}
            );
          }
          return RSVP.all([
            gadget.translate('All work caught up!'),
            gadget.getUrlForList(url_for_parameter_list)
          ]);
        })
        // Add in the page
        .push(function (result_list) {
          var line_list = [],
            url_list = result_list[1],
            i;
          for (i = 2; i < url_list.length; i += 1) {
            line_list.push({
              link: url_list[i],
              // Remove the counter from the title
              title: action_list[i - 2].name,
              count: action_list[i - 2].count
            });
          }

          gadget.element.querySelector('.document_list').innerHTML =
            table_template({
              document_list: line_list,
              empty_text: result_list[0]
            });
          return gadget.updateHeader({
            page_title: 'Worklist',
            page_icon: 'tasks',
            front_url: url_list[0],
            language_url: url_list[1]
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, Handlebars, URI));