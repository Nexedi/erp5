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
    .allowPublicAcquisition("getMainInnerHTML", function () {
      return this.main_element.innerHTML;
    })
    .allowPublicAcquisition("showPage", function () {
      this.element.hidden = false;

    })
    .declareService(function () {
      var gadget = this,
        body = gadget.element;
      // Clear the DOM
      while (body.firstChild) {
        body.firstChild.remove();
      }
      return gadget.declareGadget('nostyle_syna.html')
        .push(function (style_gadget) {
          body.appendChild(style_gadget.element);
        });
    });

}());