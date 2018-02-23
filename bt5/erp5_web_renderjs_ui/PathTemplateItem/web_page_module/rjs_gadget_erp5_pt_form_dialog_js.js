/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, URI, calculatePageTitle, Blob, URL, document, jIO, Handlebars, ensureArray */
(function (window, rJS, RSVP, URI, calculatePageTitle, Blob, URL, document, jIO, Handlebars, ensureArray) {
  "use strict";

  function submitDialog(gadget, submit_action_id, is_update_method) {
    var form_gadget = gadget,
      action = form_gadget.state.erp5_document._embedded._view._actions.put,
      form_id = form_gadget.state.erp5_document._embedded._view.form_id,
      dialog_id = form_gadget.state.erp5_document._embedded._view.dialog_id,
      redirect_to_parent;

    return form_gadget.notifySubmitting()
      .push(function () {
        return form_gadget.getDeclaredGadget("erp5_form");
      })
      .push(function (erp5_form) {
        return erp5_form.getContent();
      })
      .push(function (content_dict) {
        var data = {},
          key;

        // In dialog form, dialog_id is mandatory and form_id is optional
        data.dialog_id = dialog_id['default'];
        if (form_id !== undefined) {
          data.form_id = form_id['default'];
        }

        data.dialog_method = form_gadget.state.form_definition[submit_action_id];
        if (is_update_method) {
          data.update_method = data.dialog_method;
        }
        //XXX hack for redirect, difined in form
        redirect_to_parent = content_dict.field_your_redirect_to_parent;
        for (key in content_dict) {
          if (content_dict.hasOwnProperty(key)) {
            data[key] = content_dict[key];
          }
        }

        return form_gadget.jio_putAttachment(
          form_gadget.state.jio_key,
          action.href,
          data
        );
      })
      .push(function (attachment) {

        if (attachment.target.response.type === "application/json") {
          // successful form save returns simple redirect and answer as JSON
          // validation errors are handled in failure branch on bottom
          return new RSVP.Queue()
            .push(function () {
              return jIO.util.readBlobAsText(attachment.target.response);
            })
            .push(function (response_text) {
              var response = JSON.parse(response_text.target.result);

              return form_gadget.notifySubmitted({
                "message": response.portal_status_message,
                "status": "success"
              });
            })
            .push(function () {
              // here we figure out where to go after form submit - indicated
              // by X-Location HTTP header placed by Base_redirect script
              var jio_key = new URI(
                attachment.target.getResponseHeader("X-Location")
              ).segment(2),
                splitted_jio_key_list,
                splitted_current_jio_key_list,
                command,
                i;

              if (redirect_to_parent) {
                return form_gadget.redirect({command: 'history_previous'});
              }
              if (form_gadget.state.jio_key === jio_key) {
                // don't update navigation history when not really redirecting
                return form_gadget.redirect({
                  command: 'change',
                  options: {
                    "jio_key": jio_key,
                    "view": "view",
                    "page": undefined
                    // do not mingle with editable because it isn't necessary
                  }
                });
              }
              // Check if the redirection goes to a same parent's subdocument.
              // In this case, do not add current document to the history
              // example: when cloning, do not keep the original document in history
              splitted_jio_key_list = jio_key.split('/');
              splitted_current_jio_key_list = form_gadget.state.jio_key.split('/');
              command = 'display_with_history';
              if (splitted_jio_key_list.length === splitted_current_jio_key_list.length) {
                for (i = 0; i < splitted_jio_key_list.length - 1; i += 1) {
                  if (splitted_jio_key_list[i] !== splitted_current_jio_key_list[i]) {
                    command = 'push_history';
                  }
                }
              } else {
                command = 'push_history';
              }

              // forced document change thus we update history
              return form_gadget.redirect({
                command: command,
                options: {
                  "jio_key": jio_key
                  // do not mingle with editable because it isn't necessary
                }
              });
            });
        }

        if (attachment.target.response.type === "application/hal+json") {
          // we have received a view definition thus we need to redirect
          // this will happen only in report/export when "Format" is unspecified
          return new RSVP.Queue()
            .push(function () {
              return form_gadget.notifySubmitted({
                "message": "Data received",
                "status": "success"
              });
            })
            .push(function () {
              return jIO.util.readBlobAsText(attachment.target.response);
            })
            .push(function (response_text) {
              return form_gadget.updateForm(JSON.parse(response_text.target.result));
            });
        }
        // response status > 200 (e.g. 202 "Accepted" or 204 "No Content")
        // mean sucessful execution of an action but does not carry any data
        // XMLHttpRequest automatically inserts Content-Type="text/xml" thus
        // we cannot test based on that
        if (attachment.target.response.size === 0 &&
            attachment.target.status > 200 &&
            attachment.target.status < 400) {
          return new RSVP.Queue()
            .push(function () {
              return form_gadget.notifySubmitted({
                "message": "Action succeeded",
                "status": "success"
              });
            })
            .push(function () {
              if (redirect_to_parent) {
                return form_gadget.redirect({command: 'history_previous'});
              }
              return form_gadget.redirect({
                command: 'change',
                options: {
                  "jio_key": form_gadget.state.jio_key,
                  "view": "view",
                  "page": undefined
                  // do not mingle with editable because it isn't necessary
                }
              });
            });
        }

        // any other attachment type we force to download because it is most
        // likely product of export/report (thus PDF, ODT ...)
        return new RSVP.Queue()
          .push(function () {
            return form_gadget.notifySubmitted({
              "message": "Data received",
              "status": "success"
            });
          })
          .push(function () {
            return form_gadget.forceDownload(attachment);
          });
      })
      .push(undefined, function (error) {
        if (error !== undefined && error.target !== undefined) {
          var error_text = 'Encountered an unknown error. Try to resubmit',
            promise_queue = new RSVP.Queue();
          // if we know what the error was, try to precise it for the user
          if (error.target.status === 400) {
            error_text = 'Input data has errors';
          } else if (error.target.status === 403) {
            error_text = 'You do not have the permissions to edit the object';
          } else if (error.target.status === 0) {
            error_text = 'Document was not saved! Resubmit when you are online or the document accessible';
          }
          // if the response type is json, then look for the status message
          // sent from the portal. We prefer to have portal_status_message in
          // all cases when we have error
          if (error.target.response.type === 'application/json') {
            promise_queue
              .push(function () {
                return jIO.util.readBlobAsText(error.target.response);
              })
              // Get the error_text from portal_status_message, if there is no
              // portal_status_message, then use the default error_text
              .push(function (response_text) {
                var response = JSON.parse(response_text.target.result);
                // If there is no portal_status_message, use the default
                // error_text
                error_text = response.portal_status_message || error_text;
              });
          }
          // display translated error_text to user
          promise_queue
            .push(function () {
              return form_gadget.notifySubmitted();
            })
            .push(function () {
              return form_gadget.translate(error_text);
            })
            .push(function (message) {
              return form_gadget.notifyChange({
                "message": message + '.',
                "status": "error"
              });
            });
          // if server validation of form data failed (indicated by response code 400)
          // we parse out field errors and display them to the user
          if (error.target.status === 400 &&
              error.target.response.type === 'application/hal+json') {
            promise_queue
              .push(function () {
                // when the server-side validation returns the error description
                if (error.target.responseType === "blob") {
                  return jIO.util.readBlobAsText(error.target.response);
                }
                // otherwise return (most-likely) textual response of the server
                return {target: {result: error.target.response}};
              })
              .push(function (event) {
                return form_gadget.displayFormulatorValidationError(JSON.parse(event.target.result));
              });
          }
          return promise_queue;
        }
        throw error;
      });
  }


  var gadget_klass = rJS(window),
    dialog_button_source = gadget_klass.__template_element
                         .getElementById("dialog-button-template")
                         .innerHTML,
    dialog_button_template = Handlebars.compile(dialog_button_source);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("updateForm", "updateForm")
    .declareAcquiredMethod("displayFormulatorValidationError", "displayFormulatorValidationError")

    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('checkValidity', function () {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.checkValidity();
        });
    }, {mutex: 'changestate'})
    .declareMethod('getContent', function () {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.getContent();
        });
    }, {mutex: 'changestate'})
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.element.querySelector('input[type="submit"]').click();
    }, {mutex: 'changestate'})

    .declareMethod('render', function (options) {
      // copy out wanted items from options and pass it to `changeState`
      return this.changeState({
        jio_key: options.jio_key,
        view: options.view,
        // ignore options.editable because dialog is always editable
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        erp5_form: options.erp5_form || {},
        // ignore global editable state (be always editable)
        show_update_button: Boolean(options.form_definition.update_action)
      });
    })

    .onStateChange(function (modification_dict) {
      var form_gadget = this,
        selector = form_gadget.element.querySelector("h3"),
        view_list = ensureArray(this.state.erp5_document._links.action_workflow),
        icon,
        title,
        i;

      title = this.state.form_definition.title;

      // XXX hardcoded...
      switch (title) {
      case "Create User":
        icon = " ui-icon-user";
        break;
      case "Create Document":
        icon = " ui-icon-file-o";
        break;
      case "Validate Workflow Action":
        icon = " ui-icon-share-alt";
        break;
      case "Submit":
        icon = " ui-icon-check";
        break;
      default:
        icon = " ui-icon-random";
        break;
      }

      // By default we display dialog form title
      for (i = 0; i < view_list.length; i += 1) {
        if (this.state.view === view_list[i].href) {
          title = view_list[i].title;
        }
      }

      return new RSVP.Queue()
        .push(function () {
          // Set the dialog button
          if (modification_dict.hasOwnProperty('show_update_button')) {
            return form_gadget.translateHtml(dialog_button_template({
              show_update_button: form_gadget.state.show_update_button
            }))
              .push(function (html) {
                form_gadget.element.querySelector('.dialog_button_container')
                                   .innerHTML = html;
              });
          }
        })
        .push(function () {
          // Calculate the h3 properties
          return RSVP.all([
            form_gadget.translate(form_gadget.state.form_definition.title),
            form_gadget.translate(title)
          ]);
        })
        .push(function (translated_title_list) {
          form_gadget.element.querySelector('input.dialogconfirm').value = translated_title_list[1];

          selector.textContent = "\u00A0" + translated_title_list[0];
          selector.className = "ui-content-title ui-body-c ui-icon ui-icon-custom" + icon;

          // Render the erp5_from
          return form_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (erp5_form) {
          var form_options = form_gadget.state.erp5_form;

          // pass own form options to the embedded form
          form_options.erp5_document = form_gadget.state.erp5_document;
          form_options.form_definition = form_gadget.state.form_definition;
          form_options.view = form_gadget.state.view;
          form_options.jio_key = form_gadget.state.jio_key;
          form_options.editable = true; // dialog is always editable

          return erp5_form.render(form_options);
        })
        .push(function () {
          // Render the headers
          return RSVP.all([
            form_gadget.getUrlFor({command: 'change', options: {page: undefined, view: undefined}}),
            calculatePageTitle(form_gadget, form_gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          form_gadget.element.querySelector('a.dialogcancel').href = all_result[0];
          return form_gadget.updateHeader({
            cancel_url: all_result[0],
            page_title: all_result[1]
          });
        });
    })

    /** The only way how to force download from javascript (working everywhere)
     * is unfortunately constructing <a> and clicking on it
     */
    .declareJob("forceDownload", function (attachment) {
      var attachment_data = attachment.target.response,
        filename = /(?:^|;)\s*filename\s*=\s*"?([^";]+)/i.exec(
          attachment.target.getResponseHeader("Content-Disposition") || ""
        ),
        a_tag = document.createElement("a");

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
    })

    .onEvent('submit', function () {
      if (this.state.has_update_action === true) {
        return submitDialog(this, "update_action", true);
      }
      return submitDialog(this, "action");
    }, false, true)

    .onEvent('click', function (evt) {
      if (evt.target.name === "action_confirm") {
        evt.preventDefault();
        return submitDialog(this, "action");
      }
      if (evt.target.name === "action_update") {
        evt.preventDefault();
        return submitDialog(this, "update_action", true);
      }
    }, false, false);

}(window, rJS, RSVP, URI, calculatePageTitle, Blob, URL, document, jIO, Handlebars, ensureArray));