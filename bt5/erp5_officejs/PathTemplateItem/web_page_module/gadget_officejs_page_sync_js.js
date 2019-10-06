/*globals window, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (window, RSVP, rJS) {
  "use strict";
  var gadget_klass = rJS(window);

  function repair_and_redirect(gadget) {
    return new RSVP.Queue()
      .push(function () {
        return gadget.getSetting('sync_reload', false);
      })
      .push(function (sync_reload) {
        if (sync_reload) {
          return gadget.setSetting('sync_reload', false)
            .push(function () {
              return gadget.reload();
            });
        }
        return new RSVP.Queue()
          .push(function () {
            if (gadget.state.cloudooo) {
              return gadget.getDeclaredGadget('cloudooo')
                .push(function (cloudooo) {
                  return cloudooo.repair();
                });
            }
          })
          .push(function () {
            if (!gadget.state.cloudooo_only) {
              return gadget.repair();
            }
          })
          .push(function () {
            if (gadget.state.redirect) {
              return gadget.redirect(window.JSON.parse(gadget.state.redirect));
            }
            return gadget.redirect({command: "display"});
          });
      });
  }

  gadget_klass
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.getSetting('conversion_dict', false)
        .push(function (result) {
          return gadget.changeState({
            auto_repair: options.auto_repair,
            redirect: options.redirect,
            cloudooo: result && true,
            cloudooo_only: options.cloudooo_only
          });
        });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this;

      return gadget.updateHeader({
        title: "Synchronize"
      })
        .push(function () {
          if (modification_dict.cloudooo) {
            return gadget.declareGadget('gadget_cloudooo.html', {
              element: gadget.element.querySelector('.cloudooo'),
              scope: "cloudooo"
            });
          }
        });
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("repair", "jio_repair")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("reload", "reload")

    .declareService(function () {
      var gadget = this;

      if (gadget.state.auto_repair) {
        return repair_and_redirect(gadget)
          .push(undefined, function (e) {
            if (e.name === "ReplicateReport") {
              throw new Error(e.toString());
            }
            throw e;
          });
      }
    });

}(window, RSVP, rJS));