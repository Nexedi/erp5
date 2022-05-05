/*globals window, RSVP, rJS, Handlebars, jIO, QueryFactory, URI*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, RSVP, rJS, Handlebars, jIO) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  rJS(window)
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareMethod('render', function (options) {
      var gadget = this;
      return gadget.jio_get(options.value.jio_key)
        .push(function (result) {
          result.display_header = options.value.display_header;
          gadget.element.querySelector(".display-financial-widget-in-listbox").innerHTML = display_widget_table(result);
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));

