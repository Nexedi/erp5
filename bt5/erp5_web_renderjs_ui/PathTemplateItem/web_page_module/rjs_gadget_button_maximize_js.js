/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('triggerMaximize', 'triggerMaximize')
    .declareAcquiredMethod("translate", "translate")

    .declareMethod('render', function () {
      var gadget = this,
          button_element = gadget.element.querySelector("button");

      return gadget.translate(
        button_element.getAttribute("data-i18n")
      ).then(function (translation) {
        button_element.textContent = translation;
      });
    })

    .onEvent('click', function (event) {
      if (event.target.tagName === "BUTTON") {
        return this.callMaximize(true);
      }
    })
    .declareJob('callMaximize', function () {
      return this.triggerMaximize(true);
    });

}(window, rJS));