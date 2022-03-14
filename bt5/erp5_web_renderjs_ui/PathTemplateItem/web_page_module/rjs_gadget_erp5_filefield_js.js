/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'p',
      type: 'file'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          editable: field_json.editable,
          required: field_json.required,
          name: field_json.key,
          title: field_json.description,
          hidden: field_json.hidden,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime(),
          multiple: field_json.multiple,
          accept: field_json.accept,
          capture: field_json.capture
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var element = this.element,
        gadget = this,
        url;
      if (gadget.state.editable) {
        url = 'gadget_html5_input.html';
      } else {
        url = 'gadget_html5_element.html';
      }
      return this.declareGadget(url, {scope: 'sub'})
        .push(function (input) {
          // Clear first to DOM, append after to reduce flickering/manip
          while (element.firstChild) {
            element.removeChild(element.firstChild);
          }
          element.appendChild(input.element);

          return input.render(gadget.state);
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