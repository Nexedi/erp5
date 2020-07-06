/*globals window, document, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .declareMethod("render", function (main_innerhtml) {
      var gadget = this;
      var div = document.createElement('div');
      div.innerHTML = main_innerhtml;
      gadget.element.querySelector('main').innerHTML = div.querySelector('div.input').firstChild.innerHTML;
    });

}());