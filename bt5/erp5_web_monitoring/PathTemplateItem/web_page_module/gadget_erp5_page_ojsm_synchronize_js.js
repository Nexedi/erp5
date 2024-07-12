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
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")

    .declareMethod("render", function (options) {
      var gadget = this, notify = {}, redirect_options;
      return this.updateHeader({
        page_title: "Monitoring Synchronization"
      })
        .push(function () {
          return gadget.getDeclaredGadget('sync_gadget')
            .push(function (sync_gadget) {
              // start synchronization now if possible (not running already)
              return sync_gadget.register({now: true});
            });
        })
        .push(function (result) {
          redirect_options = {"page": "ojsm_dispatch", "notify_msg": result.msg, "notify_type": result.type};
          notify.msg = result.msg;
          notify.type = result.type;
          if (notify.type === "error") {
            // drop master url list settings if sync failed
            return gadget.setSetting('latest_master_url_list', undefined)
              .push(function () {
                return gadget.setSetting('master_url_list', undefined);
              });
          }
        })
        .push(function () {
          if (options.reset === "1") {
            // reset redirections
            return gadget.setSetting("sync_redirect_options", undefined)
              .push(function () {
                return gadget.redirect({
                  "command": "display",
                  "options": redirect_options
                });
              });
          }
          return gadget.getSetting('sync_redirect_options')
            .push(function (redirect_dict) {
              if (redirect_dict) {
                redirect_dict.msg = notify.msg;
                redirect_dict.type = notify.type;
                redirect_options = redirect_dict;
                return gadget.setSetting("sync_redirect_options", undefined);
              }
            })
            .push(function () {
              return gadget.redirect({
                "command": "display",
                "options": redirect_options
              });
            });
        });
    });
}(window, rJS));