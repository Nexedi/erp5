/*global window, rJS, RSVP, domsugar, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, domsugar, URI) {
  "use strict";

  rJS(window)
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
              {command: 'display'}
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
            // HARDCODED: most erp5's module listboxes are named 'listbox'
            // Drop the sort parameter, to speed up the calculation
            display_options['field_listbox_sort_list:json'] = undefined;
            url_for_parameter_list.push(
              {command: 'push_history_stored_state', options: display_options}
            );
          }
          return RSVP.all([
            gadget.translate('All work caught up!'),
            gadget.getUrlForList(url_for_parameter_list)
          ]);
        })
        // Add in the page
        .push(function (result_list) {
          var url_list = result_list[1],
            i,
            dom_list = [];

          for (i = 2; i < url_list.length; i += 1) {
            dom_list.push(domsugar('li', {class: 'ui-li-has-count'}, [
              domsugar('a', {href: url_list[i]}, [
                action_list[i - 2].name,
                ' ',
                domsugar('span', {class: 'ui-li-count',
                                  text: action_list[i - 2].count})
              ])
            ]));
          }

          if (dom_list.length) {
            domsugar(gadget.element.querySelector('.document_list'), [
              domsugar('ul', {class: 'document-listview'}, dom_list)
            ]);
          } else {
            domsugar(gadget.element.querySelector('.document_list'), [
              domsugar('div', {class: 'worklist-empty'}, [
                domsugar('h2', {text: result_list[0]}),
                domsugar('img', {src: 'gadget_erp5_worklist_empty.svg'})
              ])
            ]);
          }

          return gadget.updateHeader({
            page_title: 'Worklist',
            page_icon: 'tasks',
            front_url: url_list[0]
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, domsugar, URI));