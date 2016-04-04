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
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var view_list,
        tab_list = [],
        gadget = this,
        erp5_document;

      return gadget.jio_getAttachment(options.jio_key, "links")
        .push(function (result) {
          var i,
            promise_list = [];
          erp5_document = result,
          view_list = erp5_document._links.view;

          // All ERP5 document should at least have one view.
          // So, no need normally to test undefined
          if (view_list.constructor !== Array) {
            view_list = [view_list];
          }

          for (i = 0; i < view_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'change', options: {
              view: view_list[i].href,
              editable: true,
              page: undefined
            }}));
          }
          promise_list.push(gadget.getUrlFor({command: 'change', options: {
            view: "view",
            page: undefined,
            editable: undefined
          }}));
          return RSVP.all(promise_list);
        })
        .push(function (all_result) {
          var i;

          for (i = 0; i < all_result.length - 1; i += 1) {
            tab_list.push({
              title: view_list[i].title,
              i18n: view_list[i].title,
              link: all_result[i]
            });
          }

          return gadget.translateHtml(table_template({
            definition_title: "Views",
            definition_i18n: "Views",
            definition_icon: "eye",
            documentlist: [{
              title: view_list[0].title,
              link: all_result[all_result.length - 1]
            }]
          }) + table_template({
            definition_title: "Editables",
            definition_i18n: "Editables",
            definition_icon: "edit",
            documentlist: tab_list
          }));
        })
        .push(function (my_translated_html) {
          gadget.props.element.innerHTML = my_translated_html;

          return RSVP.all([
            gadget.getUrlFor({command: 'change', options: {
              page: undefined
            }}),
            gadget.getUrlFor({command: 'change', options: {page: "breadcrumb"}})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            back_url: url_list[0],
            page_title: erp5_document.title,
            breadcrumb_url: url_list[1]
          });
        });
    });

}(window, rJS, RSVP, Handlebars));