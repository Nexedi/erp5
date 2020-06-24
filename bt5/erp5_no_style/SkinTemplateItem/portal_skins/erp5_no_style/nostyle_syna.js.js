/*globals window, document, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getMainInnerHTML", "getMainInnerHTML")
    .declareAcquiredMethod("showPage", "showPage")

    .declareService(function () {
      var gadget = this;
      return gadget.getMainInnerHTML()
        .push(function (main_innerhtml) {
          var div = document.createElement('div');
          div.innerHTML = main_innerhtml;
          gadget.element.querySelector('div.py-5').innerHTML = div.querySelector('div.input').firstChild.innerHTML;
          return RSVP.delay(50);
        })

        .push(function () {
          return gadget.showPage();
        });

    });

}());