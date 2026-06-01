/*jslint nomen: true, indent: 2, maxerr: 6 */
/*global window, rJS, Handlebars, document, RSVP */
(function (window, rJS, Handlebars, document, RSVP) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,

    header_button_template = Handlebars.compile(template_element
                                                  .getElementById("header-button-template")
                                                  .innerHTML);

  gadget_klass
    .setState({
      loaded: false,
      modified: false,
      submitted: true,
      error: false,
      title_icon: undefined,
      title_url: undefined
    })
    //////////////////////////////////////////////
    // acquired methods
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .declareAcquiredMethod("triggerPanel", "triggerPanel")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('notifyLoaded', function () {
      return this.changeState({
        loaded: true
      });
    })
    .declareMethod('notifyLoading', function () {
      return this.changeState({
        loaded: false
      });
    })
    .declareMethod('notifySubmitted', function () {
      return this.changeState({
        submitted: true,
        // Change modify here, to allow user to redo some modification and being correctly notified
        modified: false
      });
    })
    .declareMethod('notifySubmitting', function () {
      return this.changeState({
        submitted: false
      });
    })
    .declareMethod('notifyError', function () {
      return this.changeState({
        loaded: true,
        submitted: true,
        error: true
      });
    })
    .declareMethod('notifyChange', function () {
      return this.changeState({
        modified: true
      });
    })
    .declareMethod('render', function (options) {
      var state = {
        error: options.error || false,
        button_icon: options.button_icon || 'bars',
        button_name: options.button_name || 'panel',
        button_class: options.button_class || undefined
      };

      return this.changeState(state);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        button,
        default_button_icon = "",
        promise_list = [];

      // Change icon based on document state
      if (modification_dict.hasOwnProperty('error') ||
          modification_dict.hasOwnProperty('loaded') ||
          modification_dict.hasOwnProperty('submitted')) {

        if (gadget.state.error) {
          default_button_icon = "exclamation";
        } else if (!gadget.state.loaded) {
          default_button_icon = "spinner";
        } else if (!gadget.state.submitted) {
          default_button_icon = "spinner";
        }
      }

      button = {
        icon: default_button_icon || gadget.state.button_icon,
        name: gadget.state.button_name
      };

      return new RSVP.Queue()
      .push(function () {
        return gadget.translateHtml(header_button_template(button));
      })
      .push(function (rendered_template) {
        gadget.element.querySelector(".ui-btn-left").innerHTML = rendered_template;
      });
    })

    .declareService(function () {
      var gadget = this,
        button = gadget.element.querySelector(".ui-btn-left");

      return window.loopEventListener(window, "scroll", false, function (event) {
        if (window.scrollY > 20) {
          if (!button.classList.contains("ui-fixed")) {
            button.classList.add("ui-fixed");
          }
        } else {
          if (button.classList.contains("ui-fixed")) {
            button.classList.remove("ui-fixed");
          }
        }
      });
    })
    //////////////////////////////////////////////
    // handle button submit
    //////////////////////////////////////////////
    .onEvent('submit', function (evt) {
      var name = evt.target[0].getAttribute("name");
      if (name === "panel") {
        return this.triggerPanel();
      }
      throw new Error("Unsupported button " + name);
    });

}(window, rJS, Handlebars, document, RSVP));