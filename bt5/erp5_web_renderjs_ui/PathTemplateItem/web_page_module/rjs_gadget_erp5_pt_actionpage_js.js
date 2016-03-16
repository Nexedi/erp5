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
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        erp5_document,
        result_list,
        action,
        view_list;

      return gadget.jio_getAttachment(options.jio_key, "links")
        .push(function (result) {
          var i,
            promise_list = [
              gadget.getUrlFor({command: 'change', options: {page: undefined}}),
              gadget.getUrlFor({command: 'change', options: {page: "breadcrumb"}})
            ];
          erp5_document = result;
          view_list = erp5_document._links.action_workflow || [];

          if (view_list.constructor !== Array) {
            view_list = [view_list];
          }

          for (i = 0; i < view_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'change', options: {view: view_list[i].href, page: undefined, editable: undefined}}));
          }
          if (erp5_document._links.action_object_clone_action) {
            view_list.push(erp5_document._links.action_object_clone_action);
            promise_list.push(gadget.getUrlFor({
              command: 'change',
              options: {
                view: erp5_document._links.action_object_clone_action.href,
                page: undefined,
                editable: true
              }
            }));
          }
          return RSVP.all(promise_list);
        })
        .push(function (all_result) {
          var i,
            tab_list = [];

          result_list = all_result;

          for (i = 2; i < all_result.length; i += 1) {
            tab_list.push({
              title: view_list[i - 2].title,
              link: all_result[i],
              i18n: view_list[i - 2].title
            });
          }
          if (erp5_document._links.action_object_clone_action) {
            action = tab_list.pop();
          }
          return gadget.translateHtml(table_template({
            definition_title: "Workflow Transitions",
            documentlist: tab_list,
            definition_i18n: "Workflow-Transitions",
            section_i18n: "Actions",
            section_title: "Actions",
            action: action
          }));
        })
        .push(function (my_translated_html) {
          gadget.props.element.innerHTML = my_translated_html;

          return gadget.updateHeader({
            back_url: result_list[0],
            page_title: erp5_document.title,
            breadcrumb_url: result_list[1]
          });
        });
    });

}(window, rJS, RSVP, Handlebars));