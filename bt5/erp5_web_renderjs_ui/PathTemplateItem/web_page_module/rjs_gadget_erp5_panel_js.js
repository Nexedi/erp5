/*jslint indent: 2, maxerr: 3 */
/*global window, rJS*/
(function (window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function toggle() {
      return this.getDeclaredGadget('subpanel')
        .push(function (sub_gadget) {
          return sub_gadget.toggle();
        });
    })
    .declareMethod('close', function close() {
      return this.getDeclaredGadget('subpanel')
        .push(function (sub_gadget) {
          return sub_gadget.close();
        });
    })

    .declareMethod('render', function render(options) {
      return this.getDeclaredGadget('subpanel')
        .push(function (sub_gadget) {
          return sub_gadget.render(options);
        });
    });

}(window, rJS));