/*globals window, RSVP, rJS, promiseEventListener, Handlebars*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (window, RSVP, rJS, promiseEventListener, Handlebars) {
  "use strict";
  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    template = Handlebars.compile(
      templater.getElementById("page-template").innerHTML
    );

  function repair_and_redirect(gadget) {
    gadget.props.element.querySelector("button").disabled = true;
    return new RSVP.Queue()
      .push(function(){
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
         .push(function (result) {
           if (result !== undefined && result.hasOwnProperty('redirect')){
             return gadget.redirect(result.redirect);
           }
           return gadget.redirect({});
         });
     });
  }

  gadget_klass
    .ready(function (g) {
      g.props = {};
      g.props.auto_repair = false;
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareMethod("render", function () {
      var gadget = this;

      if (arguments[0].auto_repair === "true") {
        gadget.props.auto_repair = true;
      }

      return gadget.updateHeader({
        title: "Synchronize"
      })
        .push(function () {
          return gadget.translateHtml(template());
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
        });
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("repair", "jio_repair")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("reload", "reload")

    .declareService(function () {
      var gadget = this;

      if (gadget.props.auto_repair === true) {
        return repair_and_redirect(gadget);
      }

      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element.querySelector('form.synchro-form'),
            'submit',
            false
          );
        })
        .push(function () {
          return repair_and_redirect(gadget);
        });
    });

}(window, RSVP, rJS, promiseEventListener, Handlebars));