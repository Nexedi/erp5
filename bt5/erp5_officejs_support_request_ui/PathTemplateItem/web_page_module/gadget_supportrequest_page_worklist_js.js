/*global window, rJS, RSVP, Handlebars, Query */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, Query) {
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
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.updateHeader({
        page_title: 'Worklist',
        page_icon: 'clipboard'
      })
        .push(function () {
          return gadget.getSetting("hateoas_url");
        })
        .push(function (hateoas_url) {
          return gadget.jio_getAttachment(
            'support_request_module',
            hateoas_url + 'support_request_module' +
               '/SupportRequestModule_getWorklistAsJson'
          );
        })
        .push(function (result) {
          /*jslint continue:true*/
          var promise_list = [],
            display_options,
            i;

          for (i = 0; i < result.length; i += 1) {
            if (result[i].action_count === 0) {
              continue;
            }
            display_options = {
              jio_key: "support_request_module",
              extended_search: Query.objectToSearchText(result[i].query),
              page: 'form',
              view: 'view'
            };

            promise_list.push(RSVP.all([
              gadget.getUrlFor({command: 'display', options: display_options}),
              // Remove the counter from the title
              result[i].action_name,
              result[i].action_count
            ]));
          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          var line_list = [], i;
          for (i = 0; i < result_list.length; i += 1) {
            line_list.push({
              link: result_list[i][0],
              title: result_list[i][1],
              count: result_list[i][2]
            });
          }
          return gadget.translateHtml(
            table_template({
              document_list: line_list
            })
          ).push(function (html) {
            gadget.element.querySelector('.document_list').innerHTML = html;
          });
        });
    });
}(window, rJS, RSVP, Handlebars, Query));