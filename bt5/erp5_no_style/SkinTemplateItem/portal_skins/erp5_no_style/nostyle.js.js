/*globals window, document, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .ready(function () {
      // Hide the page as fast as possible
      this.element.hidden = true;
      this.main_element = this.element.querySelector('main');
    })
    .declareService(function () {
      var gadget = this,
        style_gadget,
        body = gadget.element;
      // Clear the DOM
      while (body.firstChild) {
        body.firstChild.remove();
      }
      return gadget.declareGadget('nostyle_syna.html')
        .push(function (result) {
          style_gadget = result;
          return style_gadget.render(gadget.main_element.innerHTML);
        })
        .push(function () {
          body.appendChild(style_gadget.element);
          gadget.element.hidden = false;
        });
    });

}());