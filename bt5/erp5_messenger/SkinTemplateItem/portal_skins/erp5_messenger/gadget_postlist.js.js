/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document,moment, FormData, jIO, Handlebars*/
(function (window, rJS, RSVP, document, moment, FormData, jIO, Handlebars) {
  "use strict";
  var gadget_klass = rJS(window),
    comment_list_template = Handlebars.compile(
      gadget_klass.__template_element.getElementById("template-document-list").innerHTML
    );

  rJS(window)

    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")

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
            erp5_form: options.erp5_form || {}
          };
          return gadget.changeState(state_dict);
        });
    })

    .onStateChange(function () {
      var gadget = this;
      // render the erp5 form
      return gadget.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          return gadget.getDeclaredGadget("editor")
            .push(function (editor) {
              return [editor, erp5_form];
            });
        })

        .push(function (gadgets) {
          var form_options = gadget.state.erp5_form,
            rendered_field,
            key,
            editor = gadgets[0],
            erp5_form = gadgets[1];
          return new RSVP.Queue()
          
          /* TODO: I get an error with this
          // I think that this rendering is the key to refresh the comment list including the new element
          // some times, after a "post comment" the list is refreshed but the new post doens't appear
          .push(
              function () {
                return RSVP.all([
                  erp5_form.render(form_options),
                  editor.render({
                    value: "",
                    key: "comment",
                    portal_type: "HTML Post",
                    editable: true,
                    editor: gadget.state.preferred_editor,
                    maximize: true
                  })
                ]);
              }
            )
          */
          
          .push(function () {
                // make our submit button editable
                var element = gadget.element.querySelector('input[type="submit"]');
                element.removeAttribute('disabled');
                element.classList.remove('ui-disabled');
              });
        })

        .push(function () {
          return gadget.jio_getAttachment(
            'post_module',
            gadget.hateoas_url + gadget.options.jio_key + "/MessengerThread_getCommentPostListAsJson"
          );
        })

        .push(function (post_list) {
          function getPostWithLinkAndLocalDate(post) {
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
          // build links with attachments and localized dates
          var queue_list = [], i = 0;
          for (i = 0; i < post_list.length; i += 1) {
            queue_list.push(getPostWithLinkAndLocalDate(post_list[i]));
          }
          return RSVP.all(queue_list);
        })
        .push(function (comment_list) {
          var comments = gadget.element.querySelector("#post_list");
          comments.innerHTML = comment_list_template({comments: comment_list});
        })

        ;

    })

    .declareJob('submitPostComment', function () {
      var gadget = this,
        submitButton = null,
        queue = null;
      submitButton = gadget.element.querySelector("input[type=submit]");
      submitButton.disabled = true;
      submitButton.classList.add("ui-disabled");

      function enableSubmitButton() {
        submitButton.disabled = false;
        submitButton.classList.remove("ui-disabled");
      }

      queue = gadget.notifySubmitted({message: "Posting comment"})
        .push(function () {
          var choose_file_html_element = gadget.element.querySelector('#attachment'),
            file_blob = choose_file_html_element.files[0],
            url = gadget.hateoas_url + gadget.options.jio_key + "/MessengerThread_createNewMessengerPost",
            data = new FormData();
          data.append("title", "hardcoded title!"); //TODO
          data.append("follow_up", gadget.options.jio_key);
          data.append("predecessor", '');
          data.append("text_content", "this is a hardcoded comment!"); //TODO
          data.append("file", file_blob); //TODO

          // reset the file upload, otherwise next comment would upload same file again
          choose_file_html_element.value = "";

          // XXX: Hack, call jIO.util.ajax directly to pass the file blob
          // Because the jio_putAttachment will call readBlobAsText, which
          // will broke the binary file. Call the jIO.util.ajax directly
          // will not touch the blob
          return jIO.util.ajax({
            "type": "POST",
            "url": url,
            "data": data,
            "xhrFields": {
              withCredentials: true
            }
          });
        })
        .push(function () {
          return new RSVP.Queue().push(function () {
            gadget.notifySubmitted({message: "Comment added", status: "success"});
          }).push(function () {
            return gadget.redirect({command: 'reload'});
          });
        }, function (e) {
          enableSubmitButton();
          return gadget.notifySubmitted({message: "Error:" + e, status: "error"});
        });
      return queue;
    })

    .onLoop(function () {
      // update relative time
      var elements = this.element.querySelectorAll("li>time");
      [].forEach.call(elements, function (element) {
        element.textContent = moment(element.getAttribute('datetime')).fromNow();
      });
    }, 5000)

    .onEvent('submit', function () {
      return this.submitPostComment();
    });

}(window, rJS, RSVP, document, moment, FormData, jIO, Handlebars));