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
        .push(function (success_case) {
          gadget.updateHeader({
            page_title: success_case.title,
          });
          
          var content = display_widget_table(success_case);
          gadget.props.element.querySelector(".display-widget")
            .innerHTML = content;
        });
    });
}(window, RSVP, rJS, Handlebars));