/*jslint nomen: true, indent: 2 */
/*global window, rJS, domsugar*/
(function (window, rJS, domsugar) {
  "use strict";

  rJS(window)

    .declareMethod('render', function (options) {
      domsugar(this.element, {html: options.value});
    });

}(window, rJS, domsugar));