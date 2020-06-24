/*globals window, document, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .ready(function () {
      this.element.textContent = 'AAAA';
      console.log('loaded');
    /*
    })
    .declareService(function () {
      var gadget = this,
        body = gadget.element;
      return new RSVP.Queue(RSVP.all([
          rJS.declareCSS("https://www.fdl-lef.org/material_design_lite.1.3.0.min.css", document.head),
          rJS.declareCSS("https://www.fdl-lef.org/font-awesome.5.1/font-awesome.5.1.css", document.head),
          rJS.declareCSS("https://www.fdl-lef.org/fdl_complexity.css", document.head)
        ]))
        .push(function () {
          var main = body.querySelector('main');

          body.innerHTML = '';
          body.appendChild(main);
          body.hidden = false;
        });

      console.log('aaaa');
      */
    });

}());