/*global window, rJS, RSVP, Handlebars, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, calculatePageTitle) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    table_template = Handlebars.compile(gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML);

  gadget_klass
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
              gadget.getUrlFor({command: 'change', options: {page: undefined}})
            ];
          erp5_document = result;
          view_list = erp5_document._links.action_workflow || [];
          action_list = erp5_document._links.action_object_action_jio || [];
          if (view_list.constructor !== Array) {
            view_list = [view_list];
          }
          if (action_list.constructor !== Array) {
            action_list = [action_list];
          }
          for (i = 0; i < view_list.length; i += 1) {
            promise_list.push(
              gadget.getUrlFor({
                command: 'change',
                options: {
                  view: view_list[i].href,
                  page: undefined
                }
              })
            );
          }
          if (erp5_document._links.action_object_clone_action) {
            action_list.push(erp5_document._links.action_object_clone_action);
          }
          for (i = 0, i_len = action_list.length; i < i_len; i += 1) {
            promise_list.push(
              gadget.getUrlFor({
                command: 'change',
                options: {
                  view: action_list[i].href,
                  page: undefined,
                  editable: true
                }
              })
            );
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
              link: all_result[i + 1],
              i18n: view_list[i].title
            });
          }
          for (i = 0; i < action_list.length; i += 1) {
            action_tab_list.push({
              title: action_list[i].title,
              link: all_result[i + 1 + view_list.length],
              i18n: action_list[i].title
            });
          }
          return RSVP.all([
            gadget.translateHtml(
              table_template({
                definition_title: "Workflow Transitions",
                definition_icon: "random",
                documentlist: tab_list,
                definition_i18n: "Workflow-Transitions"
              }) + table_template({
                definition_i18n: "Actions",
                definition_title: "Actions",
                definition_icon: "gear",
                documentlist: action_tab_list
              })
            ),
            calculatePageTitle(gadget, erp5_document)
          ]);
        })
        .push(function (last_result_list) {
          gadget.element.innerHTML = last_result_list[0];

          return gadget.updateHeader({
            back_url: result_list[0],
            page_title: last_result_list[1]
          });
        });
    });

}(window, rJS, RSVP, Handlebars, calculatePageTitle));