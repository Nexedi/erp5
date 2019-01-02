/*global window, rJS, RSVP, Handlebars */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
      template_element = gadget_klass.__template_element,
      result_list_template = Handlebars.compile(
        template_element
        .getElementById("result-list-template")
        .innerHTML
      );

  gadget_klass
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .declareMethod('render', function (options) {
      var gadget = this,
          result_inner_html = "";

      return gadget.getUrlFor({command: 'display_erp5_action', options: {jio_key: "foo_module", page: "empty_mass_action"}})
        .push(function (link) {
          gadget.element.querySelector(".result-block").innerHTML = result_list_template({
            "i": 0,
            "link": link
          });
        });
    });

}(window, rJS, RSVP, Handlebars));