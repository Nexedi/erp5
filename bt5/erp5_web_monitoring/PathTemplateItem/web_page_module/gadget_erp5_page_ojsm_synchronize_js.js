/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")

    .declareMethod("render", function () {
      var gadget = this;
      return this.updateHeader({
          page_title: "Monitoring Synchronization"
        })
        .push(function () {
          return gadget.getDeclaredGadget('sync_gadget')
            .push(function (sync_gadget) {
              // start synchronization now if possible (not running already)
              return sync_gadget.registerSync({now: true});
            });
        })
        .push(function () {
          gadget.redirect({command: "change", options: {page: "ojsm_status_list"}});
        });
    });
}(window, rJS));
