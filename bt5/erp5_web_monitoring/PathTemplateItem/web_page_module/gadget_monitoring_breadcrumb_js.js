/*global document, window, rJS, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, document, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    breadcrumb_template = Handlebars.compile(
      templater.getElementById("breadcrumb-template").innerHTML
    );

  gadget_klass
    .declareMethod("render", function (options) {
      var gadget = this,
        i,
        content;
      if (options.url_list === undefined) {
        options.url_list = [];
      }
      content = breadcrumb_template({
        url_list: options.url_list,
        icon: options.icon || ''
      });

      gadget.element.querySelector('.monitoring-breadcrumb')
        .innerHTML = content;
      return;
    });

}(window, document, rJS, Handlebars));