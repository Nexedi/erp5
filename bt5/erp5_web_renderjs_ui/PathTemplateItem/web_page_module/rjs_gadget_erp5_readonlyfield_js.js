/*global window, rJS*/
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'p'
    })

    .declareMethod('render', function render(options) {
      var field_json = options.field_json || {},
        state_dict = {
          text_content: field_json.value || field_json.default || "",
          id: field_json.key,
          hidden: field_json.hidden
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function onStateChange() {
      var gadget = this;
      return this.getDeclaredGadget('p')
        .push(function (input) {
          return input.render(gadget.state);
        });
    })

    .declareMethod('getContent', function () {
      // A readonly field never modifies a document
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS));