/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'p'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          value: field_json.value || field_json.default || "",
          editable: field_json.editable,
          required: field_json.required,
          id: field_json.key,
          name: field_json.key,
          title: field_json.title,
          type: 'password',
          hidden: field_json.hidden,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };
      state_dict.text_content = state_dict.value;
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
          var state;
          if (gadget.state.editable) {
            state = gadget.state;
          } else {
            state = {
              tag: gadget.state.tag,
              text_content: '*****'
            };
          }
          return input.render(state);
        });
    })

    .declareMethod('getContent', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.getContent();
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

}(window, rJS));