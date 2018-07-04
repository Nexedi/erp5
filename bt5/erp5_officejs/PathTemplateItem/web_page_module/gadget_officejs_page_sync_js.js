/*globals window, RSVP, rJS, Handlebars*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (window, RSVP, rJS, Handlebars) {
  "use strict";
  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    template = Handlebars.compile(
      templater.getElementById("page-template").innerHTML
    );

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
        return gadget.repair()
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
      return this.changeState({
        auto_repair: options.auto_repair,
        redirect: options.redirect
      });
    })
    .onStateChange(function () {
      var gadget = this;

      return gadget.updateHeader({
        title: "Synchronize"
      })
        .push(function () {
          return gadget.translateHtml(template());
        })
        .push(function (html) {
          gadget.element.innerHTML = html;
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
        return repair_and_redirect(gadget);
      }
    });

}(window, RSVP, rJS, Handlebars));