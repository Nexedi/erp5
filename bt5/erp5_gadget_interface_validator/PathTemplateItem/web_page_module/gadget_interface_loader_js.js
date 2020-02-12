/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global rJS, window, document*/
(function (window, rJS, document) {
  "use strict";

  rJS(window)
    .declareMethod("declareGadgetToCheck", function (url) {
      // return;
      console.log('declareGadgetToCheck', url);
      this.element.innerHTML = '';
      var div = document.createElement('div'),
        gadget = this;
      this.element.appendChild(div);
      return new RSVP.Queue()
        .push(function () {
          return gadget.declareGadget(url, {
            scope: 'gadget_to_check',
            sandbox: 'iframe',
            element: div
          });
        })
        .push(function () {
          // Do not return the loaded gadget.
          // XXX This seems to break rJS iframe communication
          console.log('loaded', url);
          // return RSVP.delay(500);
        }, function (error) {
          console.log('failed', error, url);
          throw error;
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