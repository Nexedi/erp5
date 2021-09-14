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
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.getUrlForList([
        // Back url
        {command: 'display'},
        // Change language
        {command: 'display', options: {page: 'language'}}
      ])
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: 'Logout',
            page_icon: 'power-off',
            front_url: url_list[0],
            language_url: url_list[1]
          });
        })
        .push(function () {
          return gadget.translate('Confirm');
        })
        .push(function (translated_text) {
          gadget.element.querySelector('input').value = translated_text;
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
          throw new Error('' + logout_url_template + ' / ' + came_from + ' / ' + UriTemplate.parse(logout_url_template).expand({came_from: came_from}));
          return gadget.redirect({
            command: 'raw',
            options: {
              url: UriTemplate.parse(logout_url_template).expand({came_from: came_from})
            }
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });
}(window, rJS, UriTemplate));