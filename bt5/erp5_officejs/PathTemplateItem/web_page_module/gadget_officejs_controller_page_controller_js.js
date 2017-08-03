/*global document, window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (g) {
          return g.triggerSubmit();
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        child_gadget_url;

      return gadget.jio_get(options.jio_key)
        .push(function (result) {

          if (result.portal_type !== undefined) {
            child_gadget_url = 'gadget_officejs_jio_' +
              result.portal_type.replace(' ', '_').toLowerCase() +
              '_view.html';
          } else {
            throw new Error('Can not display document: ' + options.jio_key);
          }

          return gadget.changeState({
            jio_key: options.jio_key,
            doc: result,
            child_gadget_url: child_gadget_url,
            editable: options.editable
          });
        });
    })
    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this;

      // Clear first to DOM, append after to reduce flickering/manip
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);

      return gadget.declareGadget(gadget.state.child_gadget_url, {element: fragment,
                                                                  scope: 'fg'})
        .push(function (form_gadget) {
          return form_gadget.render({
            jio_key: gadget.state.jio_key,
            doc: gadget.state.doc,
            editable: gadget.state.editable
          });
        });
    });

}(document, window, rJS));