/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global rJS, window, document*/
(function (window, rJS, document) {
  "use strict";

  rJS(window)
    .declareMethod("declareGadgetToCheck", function (url) {
      var div = document.createElement('div'),
        gadget = this;
      this.element.innerHTML = '';
      this.element.appendChild(div);
      return gadget.declareGadget(url, {
        scope: 'gadget_to_check',
        sandbox: 'iframe',
        element: div
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

}(window, rJS, document));