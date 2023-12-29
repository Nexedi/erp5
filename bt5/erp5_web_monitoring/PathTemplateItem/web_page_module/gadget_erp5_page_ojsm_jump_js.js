/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML,
    table_template = Handlebars.compile(source);

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        promise_list = [];

      options.page = options.jump_page;
      promise_list.push(gadget.getUrlFor({command: "display", options: options}));
      if (options.title !== undefined &&
          options.search_page !== undefined) {
        promise_list.push(gadget.getUrlFor({command: "display", options: {
          page: options.search_page,
          portal_type: options.portal_type,
          extended_search: options.title
        }}));
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          var tab_list = [];

          tab_list.push({
            title: options.view_title || options.jio_key,
            link: result_list[0],
            i18n: options.view_title || options.jio_key
          });
          if (result_list.length > 1) {
            tab_list.push({
              title: options.title + " Promises",
              link: result_list[1],
              i18n: options.title + " Promises"
            });
          }
          return RSVP.all([
            gadget.translateHtml(table_template({
              definition_title: "Jumps",
              documentlist: tab_list,
              definition_i18n: "Jumps"
            })),
            gadget.getUrlFor({command: 'history_previous'})
          ]);
        })
        .push(function (last_result_list) {
          gadget.element.innerHTML = last_result_list[0];

          return gadget.updateHeader({
            back_url: last_result_list[1],
            page_title: options.title + ": Jump to URL"
          });
        });
    });

}(window, rJS, RSVP, Handlebars));