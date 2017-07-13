/*global window, rJS, RSVP, calculatePageTitle, FormData, URI, jIO*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
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
      return this.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          var form_options = gadget.state.erp5_form,
            rendered_form = gadget.state.erp5_document._embedded._view,
            rendered_field,
            key;

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

          return erp5_form.render(form_options);
        })

        // render the header
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'change', options: {editable: true}}),
            gadget.getUrlFor({command: 'change', options: {page: "action"}}),
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.getUrlFor({command: 'change', options: {page: "tab"}}),
            gadget.state.erp5_document._links.action_object_report_jio ?
                gadget.getUrlFor({command: 'change', options: {page: "export"}}) :
                "",
            calculatePageTitle(gadget, gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          return gadget.updateHeader({
            edit_url: all_result[0],
            actions_url: all_result[1],
            selection_url: all_result[2],
            previous_url: all_result[3],
            next_url: all_result[4],
            tab_url: all_result[5],
            export_url: all_result[6],
            page_title: all_result[7]
          });
        })
        .push(function () {
          return gadget.jio_getAttachment(
            'post_module',
            gadget.hateoas_url + 'post_module/PostModule_getAscendingRelatedPostListAsJson'
              + "?follow_up=" + gadget.options.jio_key
          );
        })
        .push(function (post_list) {
          var i,  // XXX abbreviation
            queue_list = [];
          if (post_list.length) {
            for (i = 0; i < post_list.length; i += 1) {
              if (post_list[i][3] !== null && post_list[i][3].indexOf("image_module") !== -1) {
                queue_list.push(gadget.getImageUrl(post_list[i][3]));
              } else if (post_list[i][3] !== null && post_list[i][3].indexOf("document_module") !== -1) {
                queue_list.push(gadget.getDocumentUrl(post_list[i][3]));
              } else {
                queue_list.push(null);
              }
            }
          }
          queue_list.push(post_list);
          return RSVP.all(queue_list);
        })
        .push(function (result_list) {
          var s = '', i, comments = gadget.element.querySelector("#post_list"),
            post_list = result_list.pop();
          if (post_list.length) {
            for (i = 0; i < post_list.length; i += 1) {
              s += '<li>' +
                'By <strong>' + post_list[i][0] + '</strong>' +
                ' - <time>' + post_list[i][1] + '</time><br/>';
              if (post_list[i][3] !== null && result_list[i] !== null) {
                post_list[i][3] = result_list[i];
              }
              if (post_list[i][2]) {
                if (post_list[i][3]) {
                  s += post_list[i][2] + '<strong>Attachment: </strong>' +
                    '<a href=\"' +
                    post_list[i][3] + '\">' + post_list[i][4] +
                    '</a>';
                } else {
                  s += post_list[i][2];
                }
              } else {
                if (post_list[i][3]) {
                  s += '<strong>Attachment: </strong>' + '<a href=\"' +
                    post_list[i][3] + '\">' + post_list[i][4] +
                    '</a>';
                }
              }
              s += '<hr id=post_item>';  // XXX XSS attack!
            }
            comments.innerHTML = s;
          } else {
            comments.innerHTML = "<p><em>No comment yet.</em></p><hr id=post_item>";
          }
        });
    })
    .declareService(function () {
      var gadget = this;
      return gadget.declareGadget('officejs_ckeditor_gadget/development/',
        {
          element: gadget.element.querySelector('.editor'),
          sandbox: 'iframe',
          scope: 'editor'
        });
    })
    .onEvent('submit', function () {
      var gadget = this,
        editor_gadget;

      return gadget.getDeclaredGadget('editor')
        .push(function (text_content_gadget) {
          editor_gadget = text_content_gadget;
          return text_content_gadget.getContent();
        })
        .push(function (data) {
          var post_content = Object.values(data)[0],
            choose_file_html_element = gadget.element.querySelector('#attachment'),
            file_blob = choose_file_html_element.files[0],
            file_upload_div = gadget.element.querySelector('#file_upload_div');
          file_upload_div.innerHTML = file_upload_div.innerHTML;
          return [post_content, file_blob];
        })
        .push(function (result) {
          // XXX: Hack, call jIO.util.ajax directly to pass the file blob
          // Because the jio_putAttachment will call readBlobAsText, which
          // will broke the binary file. Call the jIO.util.ajax directly
          // will not touch the blob
          var url = gadget.hateoas_url + "post_module/PostModule_createHTMLPost",
            data = new FormData();
          data.append("follow_up", gadget.options.jio_key);
          data.append("predecessor", '');
          data.append("data", result[0]);
          data.append("file", result[1]);
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
          return RSVP.all([
            editor_gadget.render({}),
            gadget.notifySubmitted("Comment added")
          ]);
        })
        .push(function () {
          return gadget.redirect({command: 'reload'});
        });
    });
}(window, rJS, RSVP, calculatePageTitle));