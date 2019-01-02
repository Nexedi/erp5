/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global rJS, window*/
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareMethod("declareGadgetToCheck", function (url) {
      return this.declareGadget(url, {
        scope: 'gadget_to_check'
      })
        .push(function () {
          // Do not return the loaded gadget.
          // XXX This seems to break rJS iframe communication
          return;
        });
    })

    .declareMethod("getGadgetToCheckInterfaceList", function () {
      return this.getDeclaredGadget('gadget_to_check')
        .push(function (gadget_to_check) {
          return gadget_to_check.getInterfaceList();
        });
    })

    .declareMethod("getGadgetToCheckMethodList", function (name) {
      return this.getDeclaredGadget('gadget_to_check')
        .push(function (gadget_to_check) {
          return gadget_to_check.getMethodList(name);
        });
    });

}(window, rJS));