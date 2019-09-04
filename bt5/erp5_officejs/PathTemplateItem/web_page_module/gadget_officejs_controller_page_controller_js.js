/*global document, window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .allowPublicAcquisition('updateDocument', function (param_list) {
      var gadget = this, content = param_list[0];
      return gadget.jio_get(gadget.state.jio_key)
        .push(function (doc) {
          var property;
          for (property in content) {
            if (content.hasOwnProperty(property)) {
              doc[property] = content[property];
            }
          }
          return gadget.jio_put(gadget.state.jio_key, doc);
        });
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
              result.portal_type.replace(/ /g, '_').toLowerCase() +
              '_view.html';
          } else {
            throw new Error('Can not display document: ' + options.jio_key);
          }

          return gadget.changeState({
            jio_key: options.jio_key,
            editable: options.editable || false,
            doc: result,
            child_gadget_url: child_gadget_url
          });
        });
    })
    .onStateChange(function (modification_dict) {
      var fragment = document.createElement('div'),
        gadget = this;
      if (!modification_dict.hasOwnProperty('child_gadget_url')) {
        return gadget.getDeclaredGadget('fg')
          .push(function (child_gadget) {
            return child_gadget.render({
              jio_key: gadget.state.jio_key,
              doc: gadget.state.doc,
              editable: gadget.state.editable
            });
          });
      }
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