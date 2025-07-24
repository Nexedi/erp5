/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, domsugar*/
(function (window, rJS, RSVP, domsugar) {
  "use strict";

  rJS(window)
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function render(options) {
      var gadget = this, jio_key = options.jio_key,
        author = options.last_post_author_dict.author_title,
        view_posts = options.view || "view_posts";
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          var posts_view = hateoas_url +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            jio_key +
            '&view=' + view_posts;
          return gadget.getUrlFor({
            command: 'push_history',
            options: {
              'jio_key': jio_key,
              'page': 'form',
              'view': posts_view,
              'last_page': true
            }
          });
        })
        .push(function (url) {
          gadget.element.appendChild(domsugar('a', {
            href: url,
            text: author
          }));
        });
    });

}(window, rJS, RSVP, domsugar));
