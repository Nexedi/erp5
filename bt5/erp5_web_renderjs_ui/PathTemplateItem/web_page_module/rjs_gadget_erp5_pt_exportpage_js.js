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
        report_list;

      return gadget.jio_getAttachment(options.jio_key, "links")
        .push(function (result) {
          var i, i_len,
            promise_list = [
              gadget.getUrlFor({command: 'change', options: {page: undefined}})
            ];
          erp5_document = result;
          report_list = erp5_document._links.action_object_report_jio || [];
          if (report_list.constructor !== Array) {
            report_list = [report_list];
          }
          for (i = 0; i < report_list.length; i += 1) {
            promise_list.push(
              gadget.getUrlFor({
                command: 'change',
                options: {
                  view: report_list[i].href,
                  page: undefined,
                  editable: options.editable
                }
              })
            );
          }
          return RSVP.all(promise_list);
        })
        .push(function (all_result) {
          var i,
            tab_list = [],
            report_tab_list = [],
            html = "";

          result_list = all_result;

          for (i = 0; i < report_list.length; i += 1) {
            report_tab_list.push({
              title: report_list[i].title,
              link: all_result[i + 1],
              i18n: report_list[i].title
            });
          }
          if (i) {
            html += table_template({
              definition_i18n: "Report",
              definition_title: "Report",
              definition_icon: "gear",
              documentlist: report_tab_list
            });
          }

          return RSVP.all([
            gadget.translateHtml(html),
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
