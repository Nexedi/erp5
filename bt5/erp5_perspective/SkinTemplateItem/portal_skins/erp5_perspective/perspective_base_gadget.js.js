/*global window, rJS, document */
/*jslint nomen: true, indent:2*/
(function (window, rJS) {
  "use strict";
  rJS(window)
    .declareMethod("render", function (options) {
      var gadget = this,
        child_html = options.child_html,
        el = document.getElementsByTagName("perspective-viewer")[0];

      gadget.getChildData(options.child_html)
        .push(function (data) {
          return gadget.getTable(data);
        })
        .push(function (table) {
          return el.load(table);
        })
        .push(function () {
          gadget.getDeclaredGadget(child_html)
            .push(function (child) {
              return child.postprocessing(el);
            });
        });

    })
    .declareMethod("getTable", function (data) {
      return window.Worker.table(data);
    })
    .declareMethod("getChildData", function (data) {
      return this.declareGadget(data, {
        scope: data
      })
        .push(function (child) {
          return child.getData();
        });
    });

}(window, rJS));