/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  function listToNewlines(lines) {
    if (Array.isArray(lines)) {return lines.join("\n"); }
    return lines;
  }

  function listToBR(lines) {
    if (Array.isArray(lines)) {return lines.join("<br/>\n"); }
    return lines;
  }

  rJS(window)

    .declareMethod('render', function (options) {
      return this.changeState(options.field_json);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        url,
        value;

      if (modification_dict.hasOwnProperty('editable')) {
        if (gadget.state.editable) {
          url = 'gadget_html5_textarea.html';
          value = listToNewlines(gadget.state.value || gadget.state.default || []);
        } else {
          url = 'gadget_html5_element.html';
          value = listToBR(gadget.state.value || gadget.state.default || []);
        }
        return this.declareGadget(url, {scope: 'sub'})
          .push(function (sub_gadget) {
            // Clear first to DOM, append after to reduce flickering/manip
            while (gadget.element.firstChild) {
              gadget.element.removeChild(gadget.element.firstChild);
            }
            gadget.element.appendChild(sub_gadget.element);
            // Use full-blown render when the widget is new
            return sub_gadget.render({
              value: value,
              name: gadget.state.key,
              editable: gadget.state.editable,
              required: gadget.state.required,
              title: gadget.state.title,
              hidden: gadget.state.hidden
            });
          });
      }

      return gadget.getDeclaredGadget('sub')
        .push(function (input) {
          if (modification_dict.hasOwnProperty("value")) {
            if (gadget.state.editable) {
              modification_dict.value = listToNewlines(modification_dict.value);
            } else {
              modification_dict.value = listToBR(modification_dict.value);
            }
          }
          // when we only receive changes we can simply pass (minimaly modified) modification dictionary
          return input.render(modification_dict);
        });
    })

    .declareMethod('getContent', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('sub')
        .push(function (sub_gadget) {
          return sub_gadget.getContent();
        });
    })

    .declareMethod('checkValidity', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.checkValidity();
          });
      }
      return true;
    });

}(window, rJS));