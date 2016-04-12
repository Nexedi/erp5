/*global window, rJS, RSVP, Handlebars, loopEventListener */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("panel-template")
                         .innerHTML,
    panel_template = Handlebars.compile(source);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (option_dict) {
      var append_class,
        append_attribute,
        placeholder = "",
        is_disabled = option_dict.disabled,
        search_gadget = this;

      if (is_disabled) {
        append_class = " ui-disabled";
        append_attribute = ' disabled="disabled';
      }
      search_gadget.props.extended_search = option_dict.extended_search;
      return new RSVP.Queue()
        .push(function () {
          return search_gadget.translateHtml(panel_template({
            widget_value: option_dict.extended_search || placeholder,
            widget_theme: option_dict.theme || "c",
            widget_status_attribute: append_attribute || placeholder,
            widget_status_class: append_class || placeholder
          }));
        })
        .push(function (my_translated_html) {
          search_gadget.props.element.querySelector("div").innerHTML =
            my_translated_html;
          return search_gadget;
        });
    })

    .declareMethod('getContent', function () {
      var input = this.props.element.querySelector('input'),
        value = input.value,
        result = {};

      if (value) {
        value = value.trim();
      }

      result[input.getAttribute('name')] = value;
      return result;
    })
    .declareService(function () {
      var gadget = this,
        clear_button = gadget.props.element.querySelector(".clear_button"),
        search_input = gadget.props.element.querySelector("input");
      return loopEventListener(
        clear_button,
        "click",
        false,
        function () {
          search_input.value = "";
          search_input.focus();
        }
      );
    });

}(window, rJS, RSVP, Handlebars, loopEventListener));