/*globals window, RSVP, rJS, Handlebars*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  rJS(window)
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    .declareMethod('render', function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_get(options.jio_key),
            gadget.getUrlFor({command: "history_previous"})
          ]);
        })
        .push(function (result_list) {
          if (result_list[0].image_url === "N/A" || result_list[0].image_url === "") {
            result_list[0].image_url = 'gadget_erp5_eci_camera.png?format=png';
            result_list[0].image_class = "custom-placeholder";
          }

          gadget.element.querySelector(".display-widget")
            .innerHTML = display_widget_table(result_list[0]);
          return gadget.updateHeader({
            page_title: result_list[0].title,
            back_url : result_list[1]
          });
        });
    });
}(window, RSVP, rJS, Handlebars));
