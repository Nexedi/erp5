/*global window, document, rJS, URI, RSVP, jIO, Blob, URL, asBoolean */
/*jslint nomen: true, indent: 2, maxerr: 3 */
/**
Page Form is a top-level gadget (a "Page") taking care of rendering form
and handling data send&receive.
*/
(function (window, document, rJS, URI, RSVP, jIO, Blob, URL, asBoolean) {
  "use strict";

  /*jslint regexp: true*/
  var warmup_gadget_done = false,
    warmup_list = [
      'gadget_erp5_label_field.html',
      'gadget_html5_element.html',
      'gadget_erp5_field_datetime.html',
      'gadget_erp5_field_string.html',
      'gadget_erp5_form.html',
      'gadget_erp5_field_float.html',
      'gadget_erp5_field_listbox.html',
      // Used in panel
      'gadget_translation.html',
      'gadget_erp5_panel.html',
      'gadget_erp5_header.html',
      'gadget_erp5_searchfield.html',
      'gadget_erp5_field_multicheckbox.html',
      'gadget_html5_input.html'
    ],
    field_warmup_list = [
      'gadget_erp5_pt_embedded_form_render.html',
      'gadget_erp5_field_integer.html',
      'gadget_erp5_field_list.html',
      'gadget_erp5_field_email.html',
      'gadget_erp5_field_formbox.html',
      'gadget_erp5_field_multilist.html',
      'gadget_erp5_field_relationstring.html',
      'gadget_erp5_field_multirelationstring.html',
      'gadget_erp5_relation_input.html',
      'gadget_erp5_field_textarea.html'
    ],
    form_list_warmup_list = [
      'gadget_erp5_pt_form_list.html'
    ],
    form_view_warmup_list = [
      'gadget_erp5_pt_form_view.html'
    ],
    form_view_editable_warmup_list = [
      'gadget_erp5_pt_form_view_editable.html',
      'gadget_html5_input.html',
      'gadget_html5_textarea.html',
      'gadget_html5_select.html'
    ],
    erp5_module_regexp = /^[^\/]+_module$/,
    erp5_portal_document_regexp = /^portal_.*\/.+$/,
    erp5_module_document_regexp = /^[^\/]+_module\/.+$/;
  /*jslint regexp: false*/

  /** Return local modifications to editable form fields after leaving the form
  for a while - for example selecting a related object.

  We use the fact that selecting a related object is still rendered by page_form
  thus gadget.state acts as a persistent storage.

  @argument result is possible current field value
  */
  function loadFormContent(gadget, result) {
    var key;
    if (gadget.state.options.form_content) {
      for (key in result) {
        if (result.hasOwnProperty(key)) {
          if (typeof result[key] === "object" &&
              result[key].hasOwnProperty("key") &&
              gadget.state.options.form_content[result[key].key]) {
            result[key]['default'] = gadget.state.options.form_content[result[key].key];
          }
        }
      }
    }
  }

  function loadListboxContent(gadget, result) {
    var key;
    if (gadget.state.options.form_content) {
      for (key in result) {
        if (result.hasOwnProperty(key)) {
          if (typeof result[key].field_gadget_param === "object" &&
              result[key].field_gadget_param.hasOwnProperty("key") &&
              gadget.state.options.form_content[result[key].field_gadget_param.key]) {
            result[key].field_gadget_param['default'] = gadget.state.options.form_content[result[key].field_gadget_param.key];
          }
        }
      }
    }
  }

  function warmupGadgetList(gadget, url_list) {
    var i;
    for (i = 0; i < url_list.length; i += 1) {
      // No need to check the result, as it will fail later
      // when rJS will try to instanciate one of this gadget
      rJS.declareGadgetKlass(rJS.getAbsoluteURL(url_list[i],
                                                gadget.__path));
    }
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("updatePanel", "updatePanel")
    .declareAcquiredMethod("refreshHeaderAndPanel", "refreshHeaderAndPanel")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")

    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function triggerSubmit() {
      return this.getDeclaredGadget('fg')
        .push(function (g) {
          return g.triggerSubmit();
        });
    }, {mutex: 'changestate'})
    .declareMethod('checkValidity', function checkValidity() {
      return this.getDeclaredGadget('fg')
        .push(function (declared_gadget) {
          return declared_gadget.checkValidity();
        });
    }, {mutex: 'changestate'})

    .declareMethod('getContent', function getContent() {
      var gadget = this;
      // no need to add runtime information in general for forms ...
      // each Form Page Template handles that on their own
      return gadget.getDeclaredGadget('fg')
        .push(function (declared_gadget) {
          return declared_gadget.getContent();
        });
    }, {mutex: 'changestate'})

    /////////////////////////////////////////////////////////////////
    // Own methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("jio_allDocs", function jio_allDocs(param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i;
          if (result.data.rows.length) {
            for (i = 0; i < result.data.rows.length; i += 1) {
              loadListboxContent(gadget, result.data.rows[i].value);
            }
          }
          return result;
        });
    })
    .allowPublicAcquisition('notifySubmit', function notifySubmit() {
      return this.triggerSubmit();
    })
    /**
     * Render obtain ERP5 Document and assigned Form Definition.
     *
     * Arguments:
     * `erp5_document` or parameters to obtain one: `jio_key`, `view`
     * `editable`
     */
    .declareMethod("render", function render(options) {
      var gadget = this,
        promise_queue = new RSVP.Queue(),
        new_state = {
          options: options,
          erp5_document: undefined,
          erp5_form: undefined,
          url: undefined,
          embedded: asBoolean(options.embedded),
          is_refresh: options.is_refresh || false
        };

      // options.editable differs when it comes from the erp5_launcher of FormBox - try to unify it here
      if (asBoolean(options.editable)) {
        options.editable = 1;
      } else {
        options.editable = 0;
      }

      if (options.hasOwnProperty('erp5_document')) {
        // if we get erp5 document during rendering then no need to fetch it
        new_state.erp5_document = options.erp5_document;
        // remove reference to erp5_document from options (and new_state.options)
        // otherwise we get infinite loop
        delete options.erp5_document;
      } else {
        promise_queue
          .push(function () {
            var result = gadget.jio_getAttachment(options.jio_key,
                                                  options.view);
            if (!warmup_gadget_done) {
              // In order to speed up initial form rendering,
              // preload most used gadgets while waiting for ERP5 form
              // calculation
              // Wait a bit for the ajax query to be triggered
              RSVP.delay(10)
                .then(function () {
                  warmupGadgetList(gadget, warmup_list);
                  if (erp5_module_document_regexp.test(options.jio_key)) {
                    // Form view is used
                    if (options.editable) {
                      warmupGadgetList(gadget, form_view_editable_warmup_list);
                    } else {
                      warmupGadgetList(gadget, form_view_warmup_list);
                    }
                    warmupGadgetList(gadget, field_warmup_list);
                  } else {
                    warmupGadgetList(gadget, form_list_warmup_list);
                  }
                });
              warmup_gadget_done = true;
            }
            return result;
          })
          .push(function (result) {
            new_state.erp5_document = result;

            if (!result._embedded) {
              return gadget.jio_getAttachment(options.jio_key, "links")
                .push(function (result2) {
                  return gadget.redirect({command: 'display_with_history', options: {
                    jio_key: options.jio_key,
                    view: result2._links.view[0].href
                  }});
                });
            }
          });
      }

      return promise_queue
        .push(function () {
          if (new_state.erp5_document._embedded._view.hasOwnProperty('_embedded')) {
            return new_state.erp5_document._embedded._view._embedded.form_definition;
          }
          var uri = new URI(new_state.erp5_document._embedded._view._links.form_definition.href);
          return gadget.jio_getAttachment(uri.segment(2), "view");
        })
        .push(function (erp5_form) {
          var url;
          if (new_state.embedded) {
            erp5_form.pt = "embedded_form_render";  // hard-coded erp5 naming
          }
          url = "gadget_erp5_pt_" + erp5_form.pt;
          // XXX Hardcoded specific behaviour for form_view
          if ((options.editable === 1) && (erp5_form.pt === "form_view")) {
            url += "_editable";
          }
          url += ".html";

          new_state.url = url;
          new_state.erp5_form = JSON.stringify(erp5_form);

          new_state.erp5_document = JSON.stringify(new_state.erp5_document);
          return gadget.changeState(new_state);
        });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var queue,
        gadget = this,
        options = gadget.state.options,
        page_template_gadget,
        is_module = erp5_module_regexp.test(gadget.state.options.jio_key),
        is_module_document = erp5_module_document_regexp.test(gadget.state.options.jio_key),
        is_portal_document = erp5_portal_document_regexp.test(gadget.state.options.jio_key),
        erp5_document = JSON.parse(gadget.state.erp5_document),
        erp5_form = JSON.parse(gadget.state.erp5_form);

      if ((!gadget.state.is_refresh) || modification_dict.hasOwnProperty('url')) {
        queue = gadget.declareGadget(gadget.state.url, {scope: "fg"});
      } else {
        queue = gadget.getDeclaredGadget("fg");
      }
      return queue
        .push(function (result) {
          page_template_gadget = result;

          var sub_options = options.fg || {};

          if (gadget.state.is_refresh) {
            // Delete the previous form content when refreshing
            // to prevent loosing user modification
            delete gadget.state.options.form_content;
          }
          loadFormContent(gadget, erp5_document._embedded._view);

          sub_options.erp5_document = erp5_document;
          sub_options.form_definition = erp5_form;
          sub_options.view = options.view;
          sub_options.action_view = options.action_view;
          sub_options.jio_key = options.jio_key; // jIO identifier of currently rendered ERP5 document
          sub_options.editable = options.editable; // form decides on editability of its fields

          return page_template_gadget.render(sub_options);
        })
        .push(function () {
          if ((!gadget.state.is_refresh) || modification_dict.hasOwnProperty('url')) {
            return page_template_gadget.getElement()
              .push(function (fragment) {
                var element = gadget.element;
                // Clear first to DOM, append after to reduce flickering/manip
                while (element.firstChild) {
                  element.removeChild(element.firstChild);
                }
                element.appendChild(fragment);
              });
          }
        })
        .push(function () {
          if (is_module) {
            return gadget.getTranslationList(["List"]);
          }
        })
        .push(function (translation_list) {
          var display_workflow_list = true;
          if (is_module) {
            if (erp5_document._links) {
              // hardcode "VIEWS: List" to hide "consistency", "history" and "metadata"
              erp5_document._links.action_object_view =
                [{"name": "view", "title": translation_list[0], "href": "view", "icon": null}];
              display_workflow_list = false;
            }
          } else if (!(is_module_document || is_portal_document)) {
            return;
          }
          return gadget.updatePanel({
            display_workflow_list: display_workflow_list,
            erp5_document: erp5_document,
            editable: gadget.state.options.editable,
            jio_key: gadget.state.options.jio_key,
            view: options.view
          });
        });
    })
    /** SubmitContent should be called by the gadget which renders submit button
        thus should handle the submit event.
        It calls getContent on the child gadget and submits those data to given
        jio_key and URL using JIO putAttachment call.
        This function handles parsing the server response, showing error/success
        messages and re-rendering the form if obtained (in success and failure case).
        Your .thenable will either receive string jio key to redirect to or undefined|null
        in case no redirect should be issued.

        Returns: on success it returns a Promise with {string} JIO key
                 on failure it throws an error with the invalid response
    */
    .allowPublicAcquisition("submitContent", function submitContent(param_list) {
      var gadget = this,
        jio_key = param_list[0],
        target_url = param_list[1],
        content_dict = param_list[2],
        result = {
          jio_key: undefined,
          view: undefined
        };

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.jio_putAttachment(jio_key, target_url, content_dict);
        })
        .push(function (attachment) {

          if (attachment.target.response.type === "application/json") {
            // successful form save returns simple redirect and an answer as JSON
            return new RSVP.Queue()
              .push(function () {
                return RSVP.all([
                  jIO.util.readBlobAsText(attachment.target.response),
                  gadget.translate('Action succeeded.')
                ]);
              })
              .push(function (result_list) {
                var response = JSON.parse(result_list[0].target.result);

                return gadget.notifySubmitted({
                  "message": response.portal_status_message || result_list[1],
                  "status": response.portal_status_level || "success"
                });
              })
              .push(function () {
                // here we figure out where to go after form submit - indicated
                // by X-Location HTTP header placed by Base_redirect script
                var uri = new URI(
                  attachment.target.getResponseHeader("X-Location")
                ),
                  redirect_jio_key = uri.segment(2);
                console.log(uri.segment(3), uri.segment(4));
                result.jio_key = redirect_jio_key;
                return result;
              });
          }

          if (attachment.target.response.type === "application/hal+json") {
            // we have received a view definition thus we need to redirect
            // this will happen only in report/export when "Format" is unspecified
            return new RSVP.Queue()
              .push(function () {
                return jIO.util.readBlobAsText(attachment.target.response);
              })
              .push(function (response_text) {
                var erp5_document = JSON.parse(gadget.state.erp5_document),
                  response_view = JSON.parse(response_text.target.result),
                  options = gadget.state.options;
                erp5_document._embedded._view = response_view;
                erp5_document._now = Date.now();  // force refresh
                // We choose render instead of changeState because the new form can use
                // different page_template (reports are setup in form_dialog but rendered
                // in report_view).
                // Validation provides document updated for error texts but uses the same
                // form thus the same view thus the same url - no DOM modifications
                //
                // We modify inplace state.options because render method uses and removes
                // erp5_document hidden in its options.
                options.erp5_document = erp5_document;
                options.is_refresh = true;
                return new RSVP.Queue()
                  .push(function () {
                    if (response_view._notification === undefined) {
                      return gadget.translate("Data received.");
                    }
                    return response_view._notification.message;
                  })
                  .push(function (translated_message) {
                    return gadget.notifySubmitted({
                      "message": translated_message,
                      "status": response_view._notification ? response_view._notification.status : "success"
                    });
                  })
                  .push(function () {
                    /* We do not need to remove _notification because we
                     * force-reload by putting _now into "hashed" document
                    if (response_view._notification !== undefined) {
                      delete response_view._notification;
                    }
                    */
                    return gadget.render(options);
                  })
                  .push(function () {
                    return gadget.refreshHeaderAndPanel();
                  })
                  .push(function () {
                    // Make sure to return nothing (previous render can return
                    // something) so the successfull handler does not receive
                    // anything which it could consider as redirect jio key.
                    return result;
                  });
              });
          }
          // response status > 200 (e.g. 202 "Accepted" or 204 "No Content")
          // means a sucessful execution of the action but does not carry any data
          // XMLHttpRequest automatically inserts Content-Type="text/xml" thus
          // we cannot test based on that
          if (attachment.target.response.size === 0 &&
              attachment.target.status > 200 &&
              attachment.target.status < 400) {
            return gadget.translate("Action succeeded.")
              .push(function (translated_message) {
                return gadget.notifySubmitted({
                  "message": translated_message,
                  "status": "success"
                });
              })
              .push(function () {
                result.jio_key = jio_key;
                return result;
              });
          }

          // any other attachment type we force to download because it is most
          // likely product of export/report (thus PDF, ODT ...)
          return gadget.translate("Data received.")
            .push(function (translated_message) {
              return gadget.notifySubmitted({
                "message": translated_message,
                "status": "success"
              });
            })
            .push(function () {
              return gadget.forceDownload(attachment);
            })
            // we could redirect back after download which was not possible
            // in the old UI but it will be a change of behaviour
            // Nicolas required this feature to be allowed
            .push(function () {
              result.jio_key = jio_key;
              return result;
            });
        })

        .push(null, function (error) {
          /** Fail branch of the JIO call. */
          var error_text = 'Encountered an unknown error. Try to resubmit.';

          if (error instanceof RSVP.CancellationError) {
            // CancellationError is thrown on "redirect" to cancel any pending
            // promises. Since it is not a failure we rethrow.
            throw error;
          }

          if (error === undefined || error.target === undefined) {
            return gadget.translate('Encountered an unknown error. Try to resubmit.')
              .push(function (translated_message) {
                return gadget.notifySubmitted({
                  'message': translated_message,
                  'status': 'error'
                });
              })
              .push(function () {
                // error was handled
                return result;
              });
          }

          // Let's display notification about the error to the user if possible
          if (error.target.status === 400) {
            error_text = 'Input data has errors.';
          } else if (error.target.status === 403) {
            error_text = 'You do not have the permissions to edit the object.';
          } else if (error.target.status === 0) {
            error_text = 'You are offline.';
          }

          // If the response is JSON, then look for the translated message sent
          // by the portal and display it to the user
          if (error.target.response && (
              error.target.response.type === 'application/json' ||
              error.target.response.type === 'application/hal+json'
            )
              ) {

            return gadget.notifySubmitted()
              .push(function () {
                return jIO.util.readBlobAsText(error.target.response);
              })
              // Translated error description must be part of the response
              .push(function (response_text) {
                var response = JSON.parse(response_text.target.result);

                if (error.target.response.type === 'application/json') {
                  // pure JSON carries only the message (deprecated)
                  // so we parse it out and return
                  return gadget.notifyChange({
                    "message": response.portal_status_message,
                    "status": "error"
                  });
                }

                if (error.target.response.type === 'application/hal+json') {
                  // HAL+JSON carries whole form definition with optional message

                  return new RSVP.Queue()
                    .push(function () {
                      if (!response._notification || !response._notification.message) {
                        // return error text from HTTP Status CODE and translate
                        return gadget.translate(error_text);
                      }
                      return response._notification.message;
                    })
                    .push(function (translated_message) {
                      return gadget.notifyChange({
                        "message": translated_message,
                        "status": response._notification ? response._notification.status : "error"
                      });
                    })
                    .push(function () {
                      var erp5_document = JSON.parse(gadget.state.erp5_document);
                      erp5_document._embedded._view = response;
                      erp5_document._now = Date.now();
                      return gadget.changeState({erp5_document: JSON.stringify(erp5_document),
                                                 is_refresh: true});
                    });
                }
              })
              .push(function () {
                // error was handled
                return result;
              });
          }

          // If the response in empty with only HTTP Status code then we display
          // our static translated error_text to the user
          return gadget.notifySubmitted()
            .push(function () {
              return gadget.translate(error_text);
            })
            .push(function (message) {
              return gadget.notifyChange({
                "message": message,
                "status": "error"
              });
            })
            .push(function () {
              // error was handled
              return result;
            });
        });
    })

    /** The only way how to force download from javascript (working everywhere)
     * is unfortunately constructing <a> and clicking on it
     */
    .declareJob("forceDownload", function forceDownload(attachment) {
      /*jslint regexp: true */
      var attachment_data = attachment.target.response,
        filename_utf8_quoted = /(?:^|;)\s*filename\*=UTF-8''?([^";]+)/i.exec(
          attachment.target.getResponseHeader("Content-Disposition") || ""
        ),
        filename = /(?:^|;)\s*filename\s*=\s*"?([^";]+)/i.exec(
          attachment.target.getResponseHeader("Content-Disposition") || ""
        ),
        a_tag = document.createElement("a");
      if (filename_utf8_quoted) {
        filename = filename_utf8_quoted;
        filename[1] = decodeURI(filename[1]);
      }
      /*jslint regexp: false */

      if (attachment.target.responseType !== "blob") {
        attachment_data = new Blob(
          [attachment.target.response],
          {type: attachment.target.getResponseHeader("Content-Type")}
        );
      }
      a_tag.style = "display: none";
      a_tag.href = URL.createObjectURL(attachment_data);
      a_tag.download = filename ? filename[1].trim() : "untitled";
      document.body.appendChild(a_tag);
      a_tag.click();

      return new RSVP.Queue()
        .push(function () {
          return RSVP.delay(10);
        })
        .push(function () {
          URL.revokeObjectURL(a_tag.href);
          document.body.removeChild(a_tag);
        });
    });


}(window, document, rJS, URI, RSVP, jIO, Blob, URL, asBoolean));