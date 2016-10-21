/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .allowPublicAcquisition("addRelationInput", function () {
      return;
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      return this.getDeclaredGadget("relation_input")
        .push(function (gadget) {
          return gadget.render(options, {index: 0});
        });
    })
    .declareMethod('getContent', function (options) {
      return this.getDeclaredGadget("relation_input")
        .push(function (gadget) {
          return gadget.getContent(options);
        });
    });

}(window, rJS));