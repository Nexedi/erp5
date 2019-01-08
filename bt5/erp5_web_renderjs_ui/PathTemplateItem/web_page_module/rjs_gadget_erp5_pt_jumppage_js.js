/*global window, rJS, RSVP, Handlebars, URI, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, URI, calculatePageTitle) {
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
        view_list;

      return gadget.jio_getAttachment(options.jio_key, "links")
        .push(function (result) {
          var i,
            promise_list = [
              gadget.getUrlFor({command: 'cancel_dialog_with_history'})
            ];
          erp5_document = result;
          view_list = erp5_document._links.action_object_jump || [];

          if (view_list.constructor !== Array) {
            view_list = [view_list];
          }

          for (i = 0; i < view_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'push_history', options: {
              extended_search: new URI(view_list[i].href).query(true).query,
              page: 'search'
            }}));
          }
          return RSVP.all(promise_list);
        })
        .push(function (all_result) {
          var i,
            tab_list = [];

          result_list = all_result;

          for (i = 1; i < all_result.length; i += 1) {
            tab_list.push({
              title: view_list[i - 1].title,
              link: all_result[i],
              i18n: view_list[i - 1].title
            });
          }
          return RSVP.all([
            gadget.translateHtml(table_template({
              definition_title: "Jumps",
              documentlist: tab_list,
              definition_i18n: "Jumps"
            })),
            calculatePageTitle(gadget, erp5_document)
          ]);
        })
        .push(function (last_result_list) {
          gadget.props.element.innerHTML = last_result_list[0];

          return gadget.updateHeader({
            back_url: result_list[0],
            page_title: last_result_list[1]
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, Handlebars, URI, calculatePageTitle));