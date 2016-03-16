/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, jQuery, RSVP, loopEventListener */
(function (window, rJS, Handlebars, $, RSVP, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // temlates
  /////////////////////////////////////////////////////////////////
  // Precompile templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source_header = gadget_klass.__template_element
                         .getElementById("panel-template-header")
                         .innerHTML,
    panel_template_header = Handlebars.compile(source_header),
    source_body = gadget_klass.__template_element
                         .getElementById("panel-template-body")
                         .innerHTML,
    panel_template_body = Handlebars.compile(source_body);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.jelement = $(element.querySelector("div"));
          g.props.render_deferred = RSVP.defer();
        });
    })

    .ready(function (g) {
      g.props.jelement.panel({
        display: "overlay",
        position: "left",
        theme: "d"
        // animate: false
      });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      this.props.jelement.panel("toggle");
    })
    .declareMethod('close', function () {
      this.props.jelement.panel("close");
    })

    .declareMethod('render', function () {
      var g = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.getUrlFor({command: 'display', options: {page: "contact"}}),
            g.getUrlFor({command: 'display', options: {page: "subscribe"}}),
            g.getUrlFor({command: 'display', options: {page: "password"}})
          ]);
        })
        .push(function (all_result) {
          // XXX: Customize panel header!
          var tmp = panel_template_header();
          tmp += panel_template_body({
            "contact_href": all_result[0],
            "subscribe_href": all_result[1],
            "password_href": all_result[2]
          });
          return tmp;
        })
        .push(function (my_translated_or_plain_html) {
          g.props.jelement.html(my_translated_or_plain_html);
          g.props.jelement.trigger("create");
          g.props.render_deferred.resolve();
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var panel_gadget = this;

      function formSubmit() {
        panel_gadget.toggle();
      }
      return new RSVP.Queue()
        .push(function () {
          return panel_gadget.props.render_deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            panel_gadget.props.element.querySelector('form'),
            'submit',
            false,
            formSubmit
          );
        });

    });

}(window, rJS, Handlebars, jQuery, RSVP, loopEventListener));