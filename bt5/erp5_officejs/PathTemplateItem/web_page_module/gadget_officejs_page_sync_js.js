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
     .push(function () {
       return gadget.repair()
     })
     .push(function (result) {
       if (result !== undefined && result.hasOwnProperty('redirect')){
         return gadget.redirect(result.redirect);
       }
       return gadget.redirect({});
     });
  }

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareMethod("render", function () {
      var gadget = this,
        auto_repair = false;

      if (arguments[0].auto_repair === "true") {
        auto_repair = true;
      }
      return gadget.updateHeader({
        title: "Synchronize"
      })
        .push(function () {
          return gadget.translateHtml(template());
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          if (auto_repair === true) {
            return repair_and_redirect(gadget);
          }
        });
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("repair", "jio_repair")

    .declareService(function () {
      var gadget = this;

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