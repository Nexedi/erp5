/*global window, rJS, domsugar */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, domsugar) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .declareMethod('render', function () {
      var gadget = this;

      return gadget.getUrlFor({
        command: 'display_erp5_action',
        options: {jio_key: "foo_module", page: "empty_mass_action"}
      })
        .push(function (link) {
          domsugar(
            gadget.element.querySelector(".result-block"),
            [
              domsugar('p', {class: 'result-0'}, [
                "Test 0",
                domsugar('a', {href: link, text: "Link 0"})
              ])
            ]
          );
        });
    });

}(window, rJS, domsugar));