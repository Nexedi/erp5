/*global window, rJS, RSVP, calculatePageTitle, FormData, URI, jIO, moment, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle, moment, Handlebars) {
  "use strict";
  var gadget_klass = rJS(window),
    comment_list_template = Handlebars.compile(
      gadget_klass.__template_element.getElementById("template-document-list").innerHTML
    );

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('getImageUrl', function (raw_url) {
      var gadget = this;
      return gadget.jio_getAttachment(raw_url, "links")
          .push(function (links) {
          var full_size_url = links._links.view[1].href;
          return gadget.getUrlFor({
            command: 'display',
            options: {
              jio_key: "image_module",
              view: full_size_url
            }
          });
        });
    })
    .declareMethod('getDocumentUrl', function (raw_url) {
      var gadget = this;
      return gadget.jio_getAttachment(raw_url, "links")
          .push(function (links) {
          var full_size_url = links._links.view[4].href;
          return gadget.getUrlFor({
            command: 'display',
            options: {
              jio_key: "document_module",
              view: full_size_url
            }
          });
        });
    })
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
            erp5_document: options.erp5_document,
            form_definition: options.form_definition,
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
            rendered_form = gadget.state.erp5_document._embedded._view,
            preferred_editor = rendered_form.your_preferred_editor.default,
            rendered_field,
            key,
            editor = gadgets[0],
            erp5_form = gadgets[1];
          // Remove all empty fields, and mark all others as non editable
          for (key in rendered_form) {
            if (rendered_form.hasOwnProperty(key) && (key[0] !== "_")) {
              rendered_field = rendered_form[key];
              if ((rendered_field.type !== "ListBox") && ((!rendered_field.default) || (rendered_field.hidden === 1) || (rendered_field.default.length === 0)
                   || (rendered_field.default.length === 1 && (!rendered_field.default[0])))) {
                delete rendered_form[key];
              } else {
                rendered_field.editable = 0;
              }
            }
          }

          form_options.erp5_document = gadget.state.erp5_document;
          form_options.form_definition = gadget.state.form_definition;
          form_options.view = gadget.state.view;
          return new RSVP.Queue()
            .push(
              function () {
                return RSVP.all([
                  erp5_form.render(form_options),
                  editor.render({
                    value: "",
                    key: "comment",
                    portal_type: "HTML Post",
                    editable: true,
                    editor: preferred_editor
                  })]);
              }
            ).push(function () {
              // make our submit button editable
              var element = gadget.element.querySelector('input[type="submit"]');
              element.removeAttribute('disabled');
              element.classList.remove('ui-disabled');
            });
        })
        // render the header
        .push(function () {
          return RSVP.hash({
            edit_url: gadget.getUrlFor({command: 'change', options: {editable: true}}),
            actions_url: gadget.getUrlFor({command: 'change', options: {page: "action"}}),
            selection_url: gadget.getUrlFor({command: 'history_previous'}),
            previous_url: gadget.getUrlFor({command: 'selection_previous'}),
            next_url: gadget.getUrlFor({command: 'selection_next'}),
            tab_url: gadget.getUrlFor({command: 'change', options: {page: "tab"}}),
            export_url: gadget.state.erp5_document._links.action_object_report_jio ?
                gadget.getUrlFor({command: 'change', options: {page: "export"}}) :
                "",
            page_title: calculatePageTitle(gadget, gadget.state.erp5_document)
          });
        })
        .push(function (header_options) {
          return gadget.updateHeader(header_options);
        })
        .push(function () {
          // set locale for momentjs
          return gadget.getSettingList(["selected_language",
            "default_selected_language"]
            ).push(function (lang_list) {
            moment.locale(lang_list[0] || lang_list[1]);
          });
        })
        .push(function () {
          return gadget.jio_getAttachment(
            'post_module',
            gadget.hateoas_url + gadget.options.jio_key + "/SupportRequest_getCommentPostListAsJson"
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
        });
    })
    .declareJob('submitPostComment', function () {
      var gadget = this,
        submitButton = null,
        queue = null;

      return gadget.getDeclaredGadget("editor")
        .push(function (e) {
          return e.getContent();
        })
        .push(function (content) {
          if (content.comment === '') {
            return gadget.notifySubmitted({message: "Post content can not be empty!"});
          }

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
                url = gadget.hateoas_url + "post_module/PostModule_createHTMLPostForSupportRequest",
                data = new FormData();
              data.append("follow_up", gadget.options.jio_key);
              data.append("predecessor", '');
              data.append("data", content.comment);
              data.append("file", file_blob);

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
        });
    })
    .onLoop(function () {
      // update relative time
      this.element.querySelectorAll("li>time").forEach(
        function (element) {
          element.textContent = moment(element.getAttribute('datetime')).fromNow();
        }
      );
    }, 5000)
    .onEvent('submit', function () {
      return this.submitPostComment();
    });
}(window, rJS, RSVP, calculatePageTitle, moment, Handlebars));