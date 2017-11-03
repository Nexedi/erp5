/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("submitContent", "submitContent")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      return this.changeState(options);
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form')
        .push(function (form_gadget) {
          return form_gadget.render(gadget.state);
        });
    })

    .declareMethod('triggerSubmit', function triggerSubmit() {
      this.element.querySelector('input[name="action_confirm"]').click();
    }, {mutex: 'changestate'})
    .allowPublicAcquisition('notifySubmit', function notifySubmit() {
      return this.triggerSubmit();
    })

    .onEvent('submit', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          return gadget.submitContent(content);
        });
    })

    .declareService(function enableButton() {
      // click event listener is now activated
      // Change the state of the gadget
      this.element.querySelector('input[name="action_confirm"]').disabled = false;
    });


}(window, rJS));