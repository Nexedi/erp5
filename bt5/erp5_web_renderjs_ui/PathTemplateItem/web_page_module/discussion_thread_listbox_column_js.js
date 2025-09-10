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
        view_posts = options.view || "view_posts",
        last_post = options.last_post || false,
        author = options.author_dict.author_title,
        url_options = {
          command: 'push_history',
          options: {
            'jio_key': jio_key,
            'page': 'form'
          }
        };
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          var posts_view = hateoas_url +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            jio_key +
            '&view=' + view_posts;
          url_options.options.view = posts_view;
          if (last_post) {
            url_options.options.last_post = last_post;
            var img = domsugar('img', {
              src: "document_icon.gif"
            });
            img.classList.add("img_latest");
            gadget.element.appendChild(img);
          }
          return gadget.getUrlFor(url_options);
        })
        .push(function (url) {
          gadget.element.appendChild(domsugar('a', {
            href: url,
            text: author
          }));
        });
    });

}(window, rJS, RSVP, domsugar));
