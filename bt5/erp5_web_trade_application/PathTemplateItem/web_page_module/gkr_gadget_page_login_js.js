/*globals window, document, RSVP, rJS, promiseEventListener, Handlebars*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (window, document, RSVP, rJS, promiseEventListener, Handlebars) {
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
        title: "Connect"
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
          gadget.props.element.querySelector("input[type=text]")
                              .focus();
          return promiseEventListener(
            gadget.props.element.querySelector('form.login-form'),
            'submit',
            false
          );
        })
        .push(function (evt) {
          gadget.props.element.querySelector("input[type=submit]")
                              .disabled = true;
          var login = evt.target.elements[0].value,
            passwd = evt.target.elements[1].value;
          Cookies.remove('__ac');
          Cookies.remove('__ac', {path:''});
          Cookies.remove('__ac', {path:'/'});
          Cookies.remove('jid');
          Cookies.remove('jid', {path:''});
          Cookies.remove('jid', {path:'/'});
          Cookies.set('__ac', window.btoa(login + ":" + passwd), {expires:36500, path:'/'})
          Cookies.set('jid', login, {expires:36500, path:'/'})
          return gadget.redirect({});
        });
    });

}(window, document, RSVP, rJS, promiseEventListener, Handlebars));