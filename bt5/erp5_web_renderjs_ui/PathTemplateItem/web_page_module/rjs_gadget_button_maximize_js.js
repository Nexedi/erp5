/*global window, rJS, domsugar */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, domsugar) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('triggerMaximize', 'triggerMaximize')
    .declareAcquiredMethod("translate", "translate")

    .declareMethod('render', function () {
      var gadget = this;

      return gadget.translate("Maximize")
        .push(function (translation) {
          return gadget.element.appendChild(
            domsugar("button", {
              "class": "ui-icon-expand ui-btn-icon-notext",
              "type": "button",
              "text": translation
            })
          );
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

}(window, rJS, domsugar));