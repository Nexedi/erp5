/*jslint indent: 2, maxerr: 3, maxlen: 80 */
/*global window, rJS */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      return this.getDeclaredGadget('access')
        .push(function (access_gadget) {
          return access_gadget.render(options);
        });
    });

}(window, rJS));