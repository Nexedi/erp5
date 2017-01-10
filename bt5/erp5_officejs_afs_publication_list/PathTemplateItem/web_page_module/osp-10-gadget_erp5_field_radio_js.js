/*global window, rJS, RSVP, document */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.props = {};
          gadget.props.element = element;
        });
    })
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('render', function (options) {
      var radio_group = this.props.element.querySelector(".radiogroup"),
        i,
        input,
        label,
        div,
        field_json = options.field_json,
        value = field_json.default || "",
        editable = field_json.editable,
        items = field_json.items;
      //the first item will always be selected if no initial default value is supplied.
      if (value === "" && field_json.select_first_item) {
        value = items[0][1];
      }
      this.props.field_json = field_json;
      for (i = 0; i < items.length; i += 1) {
        div = document.createElement("div");
        div.setAttribute("class", "ui-field-contain");
        input = document.createElement("input");
        input.setAttribute("class", "ui-btn");
        input.setAttribute("type", "radio");
        input.setAttribute("name", field_json.key);
        input.setAttribute("value", items[i][1]);
        if (items[i][1] === value) {
          input.setAttribute("checked", true);
        }
        if (editable === 0) {
          input.setAttribute("class", "ui-btn ui-state-disabled");
        }
        label = document.createElement("label");
        label.setAttribute('for', items[i][0]);
        label.textContent = items[i][0];
        label.setAttribute('data-i18n', items[i][0]);
        
        div.appendChild(label);
        div.appendChild(input);
        radio_group.appendChild(div);
      }
      radio_group.setAttribute("data-type", field_json.orientation);
    })
    .declareMethod('checkValidity', function () {
      var gadget = this,
        json_field = gadget.props.field_json;
      return new RSVP.Queue()
        .push(function () {
          return gadget.notifyValid();
        })
        .push(function () {
          return gadget.getContent();
        })
        .push(function (result) {
          if (json_field.required && !result.hasOwnProperty(json_field.key)) {
            return gadget.notifyInvalid("This field is required");
          }
          return true;
        });
    })
    .declareMethod('getContent', function () {
      var inputs = this.props.element.querySelectorAll("input"),
        i,
        result = {};
      for (i = 0; i < inputs.length; i += 1) {
        if (inputs[i].checked === true) {
          result[this.props.field_json.key] = inputs[i].value;
          break;
        }
      }
      return result;
    });
}(window, rJS, RSVP));