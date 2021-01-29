/*global window, rJS, RSVP, domsugar, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, domsugar, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  // copy from wiki
  function SearchError(message, status_code) {
    if ((message !== undefined) && (typeof message !== "string")) {
      throw new TypeError('You must pass a string.');
    }
    this.message = message || "Default Message";
    this.status_code = status_code || 500;
  }
  SearchError.prototype = new Error();
  SearchError.prototype.constructor = SearchError;

  function createMultipleSimpleOrQuery(key, value_list) {
    var i,
      query_list = [];
    if (!Array.isArray(value_list)) {
      value_list = [value_list];
    }
    for (i = 0; i < value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        operator: "=",
        type: "simple",
        value: value_list[i]
      }));
    }
    if (value_list.len === 1) {
      return query_list[0];
    }
    return new ComplexQuery({
      operator: "OR",
      query_list: query_list,
      type: "complex"
    });
  }

  function getFirstDocumentValue(gadget, select_list, search_dict) {
    var query_list = Object.entries(search_dict).map(function (tuple) {
      return createMultipleSimpleOrQuery(tuple[0], tuple[1]);
    });
    return gadget.jio_allDocs({
      select_list: select_list,
      query: Query.objectToSearchText(
        new ComplexQuery({
          operator: "AND",
          type: "complex",
          query_list: query_list
        })
      ),
        limit: 1
      })
      .push(function (result) {
        if (result.data.rows.length === 0) {
          throw new SearchError(
            'Can find document matching ' + JSON.stringify(search_dict),
            404
          );
        }
        return result.data.rows[0].value;
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("updatePanel", "updatePanel")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        extra_action_dict = {},
        parameter_list = [];

      parameter_list.push({
        command: 'display_with_history',
        options: {
          page: "osoe_new"
        }
      });
      parameter_list.push({
        command: 'display_with_history',
        options: {
          page: 'osoe_report'
        }
      });
      parameter_list.push({
        command: 'display_erp5_action_with_history',
        options: {
          jio_key: 'document_module',
          page: 'contribute_file',
          keep_history: true
        }
      });
      return gadget.getUrlForList(parameter_list)
      .push(function (href_list) {
        return gadget.changeState({
          extra_menu_dict: {
            'Link' : {
              'icon': 'link',
              'action_list': [
                {
                  "title" : "New",
                  "class_name" : "ui-btn-icon-top ui-icon-plus"
                },
                {
                  'title' : 'Report',
                  'class_name' : 'ui-icon ui-icon-bar-chart-o'
                },
                {
                  'title' : 'Contribute',
                  'class_name' : 'ui-btn-icon-top ui-icon-file'
                }
              ],
              'href_list': href_list
            }
          },
          homepage: 'my_homepage'
        });
      });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        doc,
        queue = new RSVP.Queue();
      if (modification_dict.homepage) {
        queue
          .push(function () {
            return RSVP.all([
              gadget.declareGadget('gadget_html_viewer.html', {element: gadget.element.querySelector('.homepage')}),
              getFirstDocumentValue(
                gadget,
                ['relative_url', 'title', 'text_content'],
                {
                  reference: modification_dict.homepage,
                  portal_type: 'Web Page',
                  validation_state: ['shared', 'shared_alive',
                                     'released', 'released_alive',
                                     'published', 'published_alive']
                })
              ]);
          })
          .push(function (result_list) {
            doc = result_list[1];
            return result_list[0].render({value: result_list[1].text_content});
          });
      }
      queue.push(function () {
        return gadget.updatePanel({
          extra_menu_dict: modification_dict.extra_menu_dict
        });
      }).push(function () {
        return gadget.updateHeader({
          page_title: 'Homepage',
          page_icon: 'home'
        });
      });
      return queue;
    });

}(window, rJS, RSVP, domsugar, SimpleQuery, ComplexQuery, Query));