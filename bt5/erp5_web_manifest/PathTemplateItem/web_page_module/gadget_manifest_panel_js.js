/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, jQuery, RSVP */
(function (window, rJS, $, RSVP, Handlebars, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // temlates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window),

    panel_full_source = gadget_klass.__template_element
                         .getElementById("panel-full-template")
                         .innerHTML,
    panel_full_template = Handlebars.compile(panel_full_source);
    
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
    .declareAcquiredMethod(
      "whoWantToDisplayThisFrontPage",
      "whoWantToDisplayThisFrontPage"
    )

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.jelement = $(element.querySelector("div.jqm-navmenu-panel"));
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

    .ready(function (my_gadget) {
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            my_gadget.whoWantToDisplayThisFrontPage("commandments"),
            my_gadget.whoWantToDisplayThisFrontPage("contents"),
            my_gadget.whoWantToDisplayThisFrontPage("components")
          ]);
        })
        .push(function (result_list) {
          return my_gadget.translateHtml(panel_full_template({
            "url_commandments": result_list[0],
            "url_contents": result_list[1],
            "url_components": result_list[2]
          }));
        })
        .push(function (my_translated_html) {
          my_gadget.props.jelement.html(my_translated_html);
          my_gadget.props.jelement.trigger("create");
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      this.props.jelement.panel("toggle");
    })

    .declareMethod('render', function () {
      return this;
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var panel_gadget,
        form_list,
        event_list,
        handler,
        i,
        len;

      function formSubmit() {
        panel_gadget.toggle();
      }

      panel_gadget = this;
      form_list = panel_gadget.props.element.querySelectorAll('form');
      event_list = [];
      handler = [formSubmit];

      // XXX: not robust - Will break when search field is active
      for (i = 0, len = form_list.length; i < len; i += 1) {
        event_list[i] = loopEventListener(
          form_list[i],
          'submit',
          false,
          handler[i]
        );
      }

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(event_list);
        });
    });

}(window, rJS, jQuery, RSVP, Handlebars, rJS.loopEventListener));
