/*globals window, document, RSVP, rJS, promiseEventListener*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (window, document, RSVP, rJS, promiseEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  rJS(window)
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
        title: "Connect"
      });
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          gadget.props.element.querySelector("input[type=text]")
                              .focus();
          return promiseEventListener(
            gadget.props.element.querySelector('form.login-form'),
            'submit',
            false
          );
        })
        .push(function (evt) {
          gadget.props.element.querySelector("button")
                              .disabled = true;
          var login = evt.target.elements[0].value,
            passwd = evt.target.elements[1].value;
          document.cookie = "__ac=" + window.btoa(login + ":" + passwd) +
                            "; path=/";
          return gadget.redirect({page:"sync"});
        });
    });

}(window, document, RSVP, rJS, promiseEventListener));