/*globals window, RSVP, rJS, promiseEventListener, Handlebars*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (window, RSVP, rJS, promiseEventListener, Handlebars) {
  "use strict";
  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    template = Handlebars.compile(
      templater.getElementById("page-template").innerHTML
    );

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
      var gadget = this;
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
          gadget.props.element.querySelector("button")
                              .disabled = true;

          return gadget.repair();
        })
        .push(function (result) {
          if (result !== undefined && result.hasOwnProperty('redirect')){
            return gadget.redirect(result.redirect);
          }
          return gadget.redirect({});
        });
    });

}(window, RSVP, rJS, promiseEventListener, Handlebars));