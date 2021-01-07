/*global window, rJS, RSVP, domsugar, SimpleQuery, ComplexQuery, Query,
         console, URL */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80, continue:true */
(function () {
  "use strict";

  var MAIN_SCOPE = 'child_scope';

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
    console.log(query_list, key, value_list);
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
    console.log(query_list);
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
          throw new Error('Can find document matching ' +
                          JSON.stringify(search_dict));
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
      if (!href.includes("/")) {
        // XXX search for reference
        to_modify_a_list.push(a_list[i]);
        url_options_list.push({
          command: 'push_history',
          options: {
            page: gadget.state.page,
            jio_key: href
          }
        });
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
        jio_key: options.jio_key || 'TEST-Js.Style.Demo.Frontpage'
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      return loadChildGadget(
        gadget,
        "gadget_editor.html",
        modification_dict.hasOwnProperty('first_render'),
        function (editor_gadget) {
          return getFirstDocumentValue(gadget, ['text_content'], {
            reference: gadget.state.jio_key,
            validation_state: ['shared', 'shared_alive',
                               'release', 'release_alive',
                               'published', 'published_alive']
          })
            .push(function (result_dict) {
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
              return gadget.updateHeader({
                page_title: 'Wiki: ' + gadget.state.jio_key,
                page_icon: 'puzzle-piece'
              });
            });
        }
      );
    });

}());