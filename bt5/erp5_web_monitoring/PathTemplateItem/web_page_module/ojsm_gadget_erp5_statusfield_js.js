/*global window, rJS, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    status_field_template = Handlebars.compile(
      templater.getElementById("template-status-field").innerHTML
    );

  gadget_klass
    .declareMethod('render', function (options) {
      var field_json = options || {},
        state_dict = {
          value: field_json.value || field_json.default || "",
          name: field_json.key,
          title: field_json.title,
          alt: field_json.description,
          hidden: field_json.hidden
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      if (this.state.hidded) {
        this.element.innerHTML = "";
      } else {
        this.element.innerHTML = status_field_template({value: this.state.value});
      }
      // check others parameters...
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, Handlebars));