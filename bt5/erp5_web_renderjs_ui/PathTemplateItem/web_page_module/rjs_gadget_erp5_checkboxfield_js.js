/*global window, rJS */
/*jslint indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({
      type: 'checkbox'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          checked: field_json.value || field_json.default,
          editable: field_json.editable,
          name: field_json.key,
          title: field_json.title
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var gadget = this;
      return this.getDeclaredGadget('sub')
        .push(function (input) {
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