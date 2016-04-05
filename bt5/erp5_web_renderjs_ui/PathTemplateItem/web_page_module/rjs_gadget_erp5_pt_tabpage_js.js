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
        jump_action_list = [],
        gadget = this,
        erp5_document,
        jump_list;

      return gadget.jio_getAttachment(options.jio_key, "links")
        .push(function (result) {
          var i,
            promise_list = [];
          erp5_document = result;
          view_list = erp5_document._links.view || [];
          jump_list = erp5_document._links.action_object_jump || [];

          // All ERP5 document should at least have one view.
          // So, no need normally to test undefined
          if (view_list.constructor !== Array) {
            view_list = [view_list];
          }
          if (jump_list.constructor !== Array) {
            jump_list = [jump_list];
          }

          promise_list.push(gadget.getUrlFor({command: 'change', options: {
            view: "view",
            page: undefined,
            editable: undefined
          }}));
          for (i = 0; i < view_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'change', options: {
              view: view_list[i].href,
              editable: true,
              page: undefined
            }}));
          }
          for (i = 0; i < jump_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'push_history', options: {
              extended_search: new URI(jump_list[i].href).query(true).query,
              page: 'search'
            }}));
          }
          return RSVP.all(promise_list);
        })
        .push(function (all_result) {
          var i, j;
          j = 1;
          for (i = 0; i < view_list.length; i += 1) {
            tab_list.push({
              title: view_list[i].title,
              i18n: view_list[i].title,
              link: all_result[j]
            });
            j += 1;
          }
          for (i = 0; i < jump_list.length; i += 1) {
            jump_action_list.push({
              title: jump_list[i].title,
              link: all_result[j],
              i18n: jump_list[i].title
            });
            j += 1;
          }
          return gadget.translateHtml(table_template({
            definition_title: "Views",
            definition_i18n: "Views",
            definition_icon: "eye",
            documentlist: [{
              title: view_list[0].title,
              link: all_result[0]
            }]
          }) + table_template({
            definition_title: "Editables",
            definition_i18n: "Editables",
            definition_icon: "edit",
            documentlist: tab_list
          }) + table_template({
            definition_title: "Jumps",
            documentlist: jump_action_list,
            definition_icon: "plane",
            definition_i18n: "Jumps"
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

}(window, rJS, RSVP, Handlebars, URI));