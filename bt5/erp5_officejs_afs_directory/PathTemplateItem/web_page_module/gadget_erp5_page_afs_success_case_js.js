/*globals window, RSVP, rJS, Handlebars*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // some parameters
  /////////////////////////////////////////////////////////////////
  var PLACEHOLDER = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAACWCA" +
    "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" +
    "uy/EEV+A9Em3PVuGWDlwAAAABJRU5ErkJggg==",

    STR = "",
    NA = "N/A",

    gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('jio_get', 'jio_get')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_get(options.jio_key);
        })
        .push(function (story) {

          if (story.image === NA || story.image === STR) {
            story.image = PLACEHOLDER;
            story.image_class = "custom-placeholder";
          }

          gadget.element.querySelector(".display-widget")
            .innerHTML = display_widget_table(story);

          return gadget.updateHeader({page_title: story.title});
        });
    });

}(window, RSVP, rJS, Handlebars));
