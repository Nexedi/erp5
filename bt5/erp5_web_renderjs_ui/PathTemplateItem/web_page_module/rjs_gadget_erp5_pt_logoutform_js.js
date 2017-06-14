/*global window, rJS, UriTemplate */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, UriTemplate) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
     .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        page_title: 'Logout',
        page_icon: 'power-off'
      })
        .push(function () {
          return gadget.translateHtml(gadget.element.innerHTML);
        })
        .push(function (my_translated_html) {
          gadget.element.innerHTML = my_translated_html;
        });
    })

    .onEvent('submit', function () {
      var gadget = this,
        logout_url_template;

      return gadget.jio_getAttachment('acl_users', 'links')
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
}(window, rJS, UriTemplate));