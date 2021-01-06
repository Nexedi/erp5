/*global window, rJS, RSVP, domsugar, SimpleQuery, ComplexQuery, Query,
         console, URL, Error */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80, continue:true */
(function () {
  "use strict";

  var MAIN_SCOPE = 'child_scope',
    document_reference_matching = /^[a-zA-Z0-9_.]+-.+/,
    document_relative_url_matching = /^[a-z]+_module\/[a-zA-Z0-9_]+/;

  function SearchError(message, status_code) {
    if ((message !== undefined) && (typeof message !== "string")) {
      throw new TypeError('You must pass a string.');
    }
    this.message = message || "Default Message";
    this.status_code = status_code || 500;
  }
  SearchError.prototype = new Error();
  SearchError.prototype.constructor = SearchError;


  function loadChildGadget(gadget, gadget_url, must_declare, callback) {
    var queue,
      child_gadget;
    if (must_declare) {
      queue = gadget.declareGadget(gadget_url, {scope: MAIN_SCOPE});
    } else {
      queue = gadget.getDeclaredGadget(MAIN_SCOPE);
    }
    return queue
      .push(function (result) {
        child_gadget = result;
        if (callback) {
          return callback(result);
        }
      })
      .push(function (result) {
        if (must_declare) {
          domsugar(gadget.element, [child_gadget.element]);
        }
        return result;
      });
  }

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
      limit: [0, 2]
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

  function rewriteHTMLPageContent(gadget, html) {
    var container = domsugar('div', {html: html}),
      i,
      a_list = container.querySelectorAll('a'),
      url_options_list = [],
      to_modify_a_list = [],
      href;
    for (i = 0; i < a_list.length; i += 1) {
      href = a_list[i].getAttribute('href');
      if (document_reference_matching.test(href) && (!href.includes('/'))) {
        // search for a document by reference reference
        to_modify_a_list.push(a_list[i]);
        url_options_list.push({
          command: 'push_history',
          options: {
            page: gadget.state.page,
            jio_key: href
          }
        });
      } else if (document_relative_url_matching.test(href) &&
                 (!href.includes('view'))) {
        // search for a document by reference reference
        to_modify_a_list.push(a_list[i]);
        url_options_list.push({
          command: 'push_history',
          options: {
            jio_key: href
          }
        });
      } else if ((href.indexOf('#!') === 0) || (href.indexOf('#/') === 0)) {
        // ERP5JS anchor links
        a_list[i].href = new URL(href, window.location.href);
      } else {
        // Compatibility layer with previous site
        a_list[i].href = new URL(href, 'https://www.erp5.com/group_section/');
      }
    }
    return gadget.getUrlForList(url_options_list)
      .push(function (result_list) {
        for (i = 0; i < to_modify_a_list.length; i += 1) {
          to_modify_a_list[i].href = new URL(result_list[i],
                                             window.location.href).href;
        }
        return container.innerHTML;
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updatePanel", "updatePanel")

    .declareMethod('triggerSubmit', function () {
      return;
    })
    ////////////////////////////////////////////////////////////////////
    // Go
    ////////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .declareMethod('render', function (options) {
      return this.changeState({
        first_render: true,
        page: options.page,
        jio_key: options.jio_key || 'NXD-ERP5JS.Home.Page',
        // Force updating the content
        render_timestamp: new Date().getTime()
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        doc;
      return loadChildGadget(
        gadget,
        "gadget_editor.html",
        modification_dict.hasOwnProperty('first_render'),
        function (editor_gadget) {
          return getFirstDocumentValue(gadget,
                                       ['relative_url', 'title',
                                        'text_content'], {
              reference: gadget.state.jio_key,
              portal_type: 'Web Page',
              validation_state: ['shared', 'shared_alive',
                                 'released', 'released_alive',
                                 'published', 'published_alive']
            })
            .push(function (result_dict) {
              doc = result_dict;
              return rewriteHTMLPageContent(gadget, result_dict.text_content);
            })
            .push(function (text_content) {
              return editor_gadget.render({
                "editor": "fck_editor",
                "editable": false,
                "maximize": "auto",
                "value": text_content
              });
            })
            .push(function () {
              return gadget.getUrlForList([
                {command: 'history_previous'},
                {command: 'display_erp5_action_with_history', options: {
                  jio_key: doc.relative_url,
                  page: 'view_editor'
                }}
              ]);
            })
            .push(function (url_list) {
              return gadget.updateHeader({
                page_title: 'Wiki: ' + doc.title,
                page_icon: 'puzzle-piece',
                front_url: url_list[0],
                edit_url: url_list[1]
              });
            })
          /*
            .push(function () {
              return gadget.updatePanel({
                erp5_document: {
                  '_links': {
                    'action_object_view': [{
                      "name": "view",
                      "title": "View",
                      "href": "view",
                      "icon": null
                    }]
                  }
                },
                jio_key: doc.relative_url,
                editable: true,
                view: null
              });
            })
            */
            .push(undefined, function (error) {
              if ((error instanceof SearchError) &&
                  (error.status_code === 404)) {
                // redirect to a search, to allow people understanding
                // why the list is broken
                return gadget.redirect({
                  command: "display_with_history",
                  options: {
                    page: "search",
                    extended_search: Query.objectToSearchText(
                      createMultipleSimpleOrQuery('reference',
                                                  gadget.state.jio_key)
                    )
                  }
                }, false);
              }

              throw error;
            });
        }
      );
    });

}());