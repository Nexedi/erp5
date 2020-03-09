/*global window, rJS, asBoolean, getFirstNonEmpty */
/*jslint indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, asBoolean, getFirstNonEmpty) {
  "use strict";

  rJS(window)
    .setState({
      type: 'checkbox',
      tag: 'p'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict,
        value;
      if (typeof field_json.default === "string") {
        value = !(field_json.default === '');
      } else {
        value = field_json.default;
      }
      state_dict = {
        checked: asBoolean(getFirstNonEmpty(field_json.value, value)),
        editable: field_json.editable,
        id: field_json.key,
        name: field_json.key,
        title: field_json.title,
        hidden: field_json.hidden,
        // Force calling subfield render
        // as user may have modified the input value
        render_timestamp: new Date().getTime()
      };
      state_dict.text_content = state_dict.checked ? '✓' : '';
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element,
        gadget = this,
        url,
        result;
      if (modification_dict.hasOwnProperty('editable')) {
        if (gadget.state.editable) {
          url = 'gadget_html5_input.html';
        } else {
          url = 'gadget_html5_element.html';
        }
        result = this.declareGadget(url, {scope: 'sub'})
          .push(function (input) {
            // Clear first to DOM, append after to reduce flickering/manip
            while (element.firstChild) {
              element.removeChild(element.firstChild);
            }
            element.appendChild(input.element);
            return input;
          });
      } else {
        result = this.getDeclaredGadget('sub');
      }
      return result
        .push(function (input) {
          return input.render(gadget.state);
        });
    })

    .declareMethod('getContent', function () {
      var context = this;
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.getContent();
          })
          .push(function (result) {
            var final_result = {};
            // Automatically add default_%s:int:0
            //   erp5/blob/8ae0706177/product/Formulator/Widget.py#L476
            final_result["default_" + context.state.name + ":int"] = 0;
            if (result[context.state.name]) {
              // from MDN checkbox spec:
              // checkbox input send 'on' value when checked
              // and is not present in the request when unchecked
              final_result[context.state.name] = 'on';
            }
            return final_result;
          });
      }
      return {};
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.checkValidity();
          });
      }
      return true;
    }, {mutex: 'changestate'});
}(window, rJS, asBoolean, getFirstNonEmpty));