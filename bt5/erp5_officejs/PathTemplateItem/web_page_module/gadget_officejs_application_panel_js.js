/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, jQuery, RSVP, loopEventListener */
(function (window, rJS, Handlebars, $, RSVP, loopEventListener) {
  "use strict";

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

    .declareAcquiredMethod("translateHtml", "translateHtml")

    // Assign the element to a variable
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })


    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.jelement = $(element.querySelector("div"));
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


    .ready(function (g) {
      return g.translateHtml(panel_template_header() + panel_template_body())
        .push(function (my_translated_or_plain_html) {
          g.props.jelement.html(my_translated_or_plain_html);
          g.props.jelement.trigger("create");
        });
    })


    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('setSetting', 'setSetting')

    .declareMethod('toggle', function () {
      this.props.jelement.panel("toggle");
    })

    .declareMethod('close', function () {
      this.props.jelement.panel("close");
    })

    .declareMethod('render', function () {
      // Extract configuration parameters stored in HTML
      // XXX Will work only if top gadget...
      var gadget = this,
        element_list =
          gadget.props.element.querySelectorAll("[data-renderjs-configuration]"),
        len = element_list.length,
        key,
        value,
        i,
        queue = new RSVP.Queue();

      function push(a, b) {
        queue.push(function () {
          return gadget.setSetting(a, b);
        });
      }

      for (i = 0; i < len; i += 1) {
        key = element_list[i].getAttribute('data-renderjs-configuration');
        value = element_list[i].textContent;
        push(key, value);
      }
      return queue;
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var panel_gadget,
        form_list,
        event_list,
        i,
        len;


      function formSubmit() {
        panel_gadget.toggle();
      }

      panel_gadget = this;
      form_list = panel_gadget.props.element.querySelectorAll('form');
      event_list = [];

      // XXX: not robust - Will break when search field is active
      for (i = 0, len = form_list.length; i < len; i += 1) {
        event_list[i] = loopEventListener(
          form_list[i],
          'submit',
          false,
          formSubmit
        );
      }

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(event_list);
        });
    });


}(window, rJS, Handlebars, jQuery, RSVP, loopEventListener));