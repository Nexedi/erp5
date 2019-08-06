/*global window, document, rJS, Quill, RSVP*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, document, React, ReactDOM, EntryPoint, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .declareJob("deferNotifySubmit", function () {
      // Ensure error will be correctly handled
      return this.notifySubmit();
    })
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareJob("deferNotifyChange", function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })

    .setState({
      is_mobile: false,
      
    })

    .declareMethod('render', function (options) {
  
      return this.changeState({
        key: options.key,
        value: options.value || "",
        editable: options.editable === undefined ? true : options.editable,
        configuration: options.configuration,
        configuration_mobile: options.configuration_mobile,
        configuration_readonly: options.configuration_readonly,
        is_responsive: (options.configuration_mobile !== undefined) ||
                       (options.configuration === undefined),
      });
    })

    .declareMethod('getContent', function () {
      var result = {};

      result[this.state.key] = JSON.stringify(this.state.component.getContent());
      return result;
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        configuration,
        chart_component = null,
        container = gadget.element.querySelector("div"),
        props = {
          data: [],
          layout: {},
          frames: [],
          url: ""
        };
      
      if (modification_dict.hasOwnProperty('configuration') ||
          modification_dict.hasOwnProperty('configuration_mobile') ||
          modification_dict.hasOwnProperty('configuration_readonly') ||
          modification_dict.hasOwnProperty('is_responsive') ||
          modification_dict.hasOwnProperty('is_mobile') ||
          modification_dict.hasOwnProperty('editable') ||
          modification_dict.hasOwnProperty('value')) {
        // Expected configuration changed.
        if ("value" in modification_dict && modification_dict.value != ""){
          props = {...props, ...JSON.parse(modification_dict.value)};
        }
        ReactDOM.unmountComponentAtNode(container);
        gadget.state.component = ReactDOM.render(React.createElement(EntryPoint.default.App, props, null), container);
      }
    });

}(window, document, React, ReactDOM, EntryPoint, rJS, RSVP));