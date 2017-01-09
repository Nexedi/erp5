/*jslint indent: 2, maxerr: 3, nomen: true, maxlen: 80 */
/*global window, rJS */
(function (window, rJS) {
  "use strict";
  rJS(window)

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .allowPublicAcquisition('trigger', function () {
      this.element.classList.toggle('visible');
    })

    .declareMethod('close', function () {
      var element = this.element;
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }
      if (element.classList.contains('visible')) {
        element.classList.remove('visible');
      }
    })

    .declareMethod('render', function (url, options) {
      this.element.classList.toggle('visible');
      return this.changeState({
        url: url,
        options: JSON.stringify(options)
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        declared_gadget;
      if (gadget.state.url && modification_dict.hasOwnProperty('options')) {
        return gadget.declareGadget(gadget.state.url,
                                    {scope: "declared_gadget"})
          .push(function (result) {
            declared_gadget = result;
            return declared_gadget.render(JSON.parse(gadget.state.options));
          })
          .push(function () {
            return gadget.close();
          })
          .push(function () {
            gadget.element.appendChild(declared_gadget.element);
            gadget.element.classList.toggle('visible');
          });
      }
    });
}(window, rJS));