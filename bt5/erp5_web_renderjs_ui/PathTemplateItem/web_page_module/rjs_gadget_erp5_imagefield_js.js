/*global window, rJS*/
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'img'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          src: field_json.default,
          alt: field_json.description || field_json.title
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var gadget = this;
      return this.getDeclaredGadget('image')
        .push(function (input) {
          return input.render(gadget.state);
        });
    })

    .declareMethod('getContent', function () {
      // An Image field never modifies a document
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS));