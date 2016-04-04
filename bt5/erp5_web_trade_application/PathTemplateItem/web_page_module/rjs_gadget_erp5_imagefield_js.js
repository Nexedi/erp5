/*global window, rJS*/
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.props = {};
          gadget.props.element = element;
        });
    })
    .declareMethod('render', function (options) {
      var image = this.props.element.querySelector(".image");
      image.src = options.field_json.default;
      image.alt = options.field_json.description || options.field_json.title;
    });
}(window, rJS));