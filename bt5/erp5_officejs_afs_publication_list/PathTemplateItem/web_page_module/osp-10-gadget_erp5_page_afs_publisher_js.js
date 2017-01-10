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
        .push(function (publisher) {
          gadget.updateHeader({
            page_title: publisher.title,
          });
          
          publisher.free_software_list.map(function (sw) {
            if (sw.commercial_support === "N/A") {
              delete sw.commercial_support;
            }
            
            if (sw.wikipedia_url === "N/A") {
              delete sw.wikipedia_url;
            }
            
            if (sw.success_case_list.length === 0 ||
                sw.success_case_list === "N/A" ||
                sw.success_case_list[0].title === "N/A" ||
                sw.success_case_list[0].title === "") {
              delete sw.success_case_list;
            }
          });
          
          var content = display_widget_table(publisher);
          gadget.props.element.querySelector(".display-widget")
            .innerHTML = content;
        });
    });
}(window, RSVP, rJS, Handlebars));