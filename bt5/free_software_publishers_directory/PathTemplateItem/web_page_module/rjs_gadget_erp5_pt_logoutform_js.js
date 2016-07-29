/*global window, rJS, RSVP, promiseEventListener, UriTemplate */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, promiseEventListener, UriTemplate) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
     .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.translateHtml(gadget.props.element.innerHTML);
        })
        .push(function (my_translated_html) {
          gadget.props.element.innerHTML = my_translated_html;
        });
    })
    .declareService(function () {
      var gadget = this,
        logout_url_template;
      // Listen to form submit
      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element.querySelector('form'),
            'submit',
            false
          );
        })
        .push(function () {
          return gadget.jio_getAttachment(
            'acl_users',
            'links'
          );
        })
        .push(function (links) {
          logout_url_template = links._links.logout.href;
          return gadget.getUrlFor({
            command: 'display',
            absolute_url: true,
            options: {}
          });
        })
        .push(function (came_from) {
          return gadget.redirect({
            command: 'raw',
            options: {
              url: UriTemplate.parse(logout_url_template).expand({came_from: came_from})
            }
          });
        });
    });
}(window, rJS, RSVP, promiseEventListener, UriTemplate));