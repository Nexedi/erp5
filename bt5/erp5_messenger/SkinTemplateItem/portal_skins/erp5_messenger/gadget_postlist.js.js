/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, moment, jIO, Handlebars, console*/
(function (window, rJS, RSVP, document, moment, jIO, Handlebars, console) {
  "use strict";
  var gadget_klass = rJS(window),
    comment_list_template = Handlebars.compile(
      gadget_klass.__template_element.getElementById("template-document-list").innerHTML
    );

  rJS(window)

    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.getSetting('hateoas_url')
        .push(function (hateoas_url) {
          gadget.hateoas_url = hateoas_url;
        })
        .push(function () {
          var state_dict = {
            id: options.jio_key,
            view: options.view,
            editable: options.editable,
            query: options.query,
            erp5_form: options.erp5_form || {}
          };
          return gadget.changeState(state_dict);
        });
    })

    .onStateChange(function () {
      var gadget = this;
      console.log("gadget.state.query:");
      console.log(gadget.state.query);
      return gadget.jio_allDocs({
        "query": gadget.state.query,
        "select_list": ["text_content", "modification_date", "local_role"],
        "sort_on": [["modification_date", "ascending"]]
      })
      .push(function (results) {
        var post_list = results.data.rows;
        function getPostWithLinkAndLocalDate(post) {
          post.date = post.value.modification_date;
          post.date_formatted = moment(post.date).format('LLLL');
          post.date_relative = moment(post.date).fromNow();
          if (post.attachment_link === null) {
            return post;
          }
          if (post.attachment_link.indexOf("image_module") !== -1) {
            return gadget.getImageUrl(post.attachment_link).push(
              function (attachment_link) {
                post.attachment_link = attachment_link;
                return post;
              }
            );
          }
          return gadget.getDocumentUrl(post.attachment_link).push(
            function (attachment_link) {
              post.attachment_link = attachment_link;
              return post;
            }
          );
        }
        var queue_list = [], i = 0;
        for (i = 0; i < post_list.length; i += 1) {
          post_list[i].user = "zope"; // problems getting Owner property
          // TODO: attachments
          post_list[i].attachment_link = null;
          post_list[i].attachment_name = null;
          queue_list.push(getPostWithLinkAndLocalDate(post_list[i]));
        }
        return RSVP.all(queue_list);
      })
      .push(function (comment_list) {
        var comments = gadget.element.querySelector("#post_list");
        comments.innerHTML = comment_list_template({comments: comment_list});
      });
    })

    .onLoop(function () {
      // update relative time
      var elements = this.element.querySelectorAll("li>time");
      [].forEach.call(elements, function (element) {
        element.textContent = moment(element.getAttribute('datetime')).fromNow();
      });
    }, 5000)

    /*.onEvent('submit', function () {
      return this.submitPostComment();
    })*/;

}(window, rJS, RSVP, document, moment, jIO, Handlebars, console));