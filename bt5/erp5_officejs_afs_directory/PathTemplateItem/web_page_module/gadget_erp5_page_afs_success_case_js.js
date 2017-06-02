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

    .declareMethod('render', function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_get(options.jio_key);
        })
        .push(function (story) {
          if (story.image === "N/A" || story.image === "") {
            story.image = 'gadget_erp5_afs_camera.png?format=png';
            story.image_class = "custom-placeholder";
          }

          gadget.element.querySelector(".display-widget")
            .innerHTML = display_widget_table(story);
          return gadget.updateHeader({page_title: story.title});
        });
    });
}(window, RSVP, rJS, Handlebars));