/*globals window, RSVP, rJS, Handlebars*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, Handlebars) {
  "use strict";

  var PLACEHOLDER = "data:image/png;base64,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",
    gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

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
            story.image = PLACEHOLDER;
            story.image_class = "custom-placeholder";
          }

          gadget.props.element.querySelector(".display-widget")
            .innerHTML = display_widget_table(story);
          return gadget.updateHeader({page_title: story.title});
        });
    });
}(window, RSVP, rJS, Handlebars));