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
        view_list,
        action_list;

      return gadget.jio_getAttachment(options.jio_key, "links")
        .push(function (result) {
          var i, i_len,
            promise_list = [
              gadget.getUrlFor({command: 'change', options: {page: undefined}}),
              gadget.getUrlFor({command: 'change', options: {page: "breadcrumb"}})
            ];
          erp5_document = result;
          view_list = erp5_document._links.action_workflow || [];
          action_list = erp5_document._links.action_object_action || [];
          if (view_list.constructor !== Array) {
            view_list = [view_list];
          }
          if (action_list.constructor !== Array) {
            view_list = [view_list];
          }

          for (i = 0; i < view_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'change', options: {view: view_list[i].href, page: undefined, editable: undefined}}));
          }
          if (erp5_document._links.action_object_clone_action) {
            action_list.push(erp5_document._links.action_object_clone_action);
          }
          for (i = 0, i_len = action_list.length; i < i_len; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'change', options: {view: action_list[i].href, page: undefined, editable: true}}));
          }
          return RSVP.all(promise_list);
        })
        .push(function (all_result) {
          var i,
            tab_list = [],
            action_tab_list = [];

          result_list = all_result;

          for (i = 0; i < view_list.length; i += 1) {
            tab_list.push({
              title: view_list[i].title,
              link: all_result[i + 2],
              i18n: view_list[i].title
            });
          }
          for (i = 0; i < action_list.length; i += 1) {
            action_tab_list.push({
              title: action_list[i].title,
              link: all_result[i + view_list.length + 2],
              i18n: action_list[i].title
            });
          }
          return gadget.translateHtml(table_template({
            definition_title: "Workflow Transitions",
            documentlist: tab_list,
            definition_i18n: "Workflow-Transitions",
            section_i18n: "Actions",
            section_title: "Actions",
            action_tab_list: action_tab_list
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