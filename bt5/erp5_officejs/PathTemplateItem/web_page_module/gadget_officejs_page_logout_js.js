/*globals window, RSVP, rJS, promiseEventListener, document, Handlebars*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (window, RSVP, rJS, promiseEventListener, document, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
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
        title: "Logout"
      })
        .push(function () {
          return gadget.translateHtml(template());
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
        });
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element.querySelector('form.logout-form'),
            'submit',
            false
          );
        })
        .push(function () {
          gadget.props.element.querySelector("input[type=submit]")
                              .disabled = true;
          document.cookie = "__ac=; path=/";
          return gadget.redirect({});
        });
    });

}(window, RSVP, rJS, promiseEventListener, document, Handlebars));