/*global window, rJS, RSVP, calculatePageTitle, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle, jIO) {
  "use strict";

  rJS(window)

    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("displayFormulatorValidationError",
                           "displayFormulatorValidationError")
    .allowPublicAcquisition("notifyChange", function () {
      return this.notifyChange({modified: true});
    })
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
      this.element.querySelector('button').click();
    })

    .declareMethod('render', function (options) {
      var state_dict = {
        jio_key: options.jio_key,
        view: options.view,
        editable: options.editable,
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        erp5_form: options.erp5_form || {},
        new_content_action: false,
        delete_action: false,
        save_action: false
      };

      if (options.erp5_document._embedded._view._actions !== undefined) {
        if (options.erp5_document._embedded._view._actions.put !== undefined) {
          state_dict.save_action = true;
        }
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var form_gadget = this;

      // render the erp5 form
      return form_gadget.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          var form_options = form_gadget.state.erp5_form;

          form_options.erp5_document = form_gadget.state.erp5_document;
          form_options.form_definition = form_gadget.state.form_definition;
          form_options.view = form_gadget.state.view;
          form_options.jio_key = form_gadget.state.jio_key;
          form_options.editable = 1;

          return erp5_form.render(form_options);
        })

        // render the header
        .push(function () {
          var new_content_action = form_gadget.state.erp5_document._links.action_object_new_content_action,
            delete_action = form_gadget.state.erp5_document._links.action_object_delete_action;

          if (new_content_action !== undefined) {
            new_content_action = form_gadget.getUrlFor({command: 'change', options: {view: new_content_action.href, editable: true}});
          } else {
            new_content_action = "";
          }

          if (delete_action !== undefined) {
            delete_action = form_gadget.getUrlFor({command: 'change', options: {view: delete_action.href}});
          } else {
            delete_action = "";
          }
          return RSVP.all([
            form_gadget.getUrlFor({command: 'change', options: {page: "tab"}}),
            form_gadget.getUrlFor({command: 'change', options: {page: "action"}}),
            new_content_action,
            form_gadget.getUrlFor({command: 'history_previous'}),
            delete_action,
            calculatePageTitle(form_gadget, form_gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          var header_dict = {
            tab_url: all_result[0],
            actions_url: all_result[1],
            add_url: all_result[2],
            selection_url: all_result[3],
            delete_url: all_result[4],
            cut_url: "",
            page_title: all_result[5]
          };
          if (form_gadget.state.save_action === true) {
            header_dict.save_action = true;
          }
          return form_gadget.updateHeader(header_dict);
        });
    })

    .onEvent('submit', function () {

      if (this.state.save_action !== true) {
        // If not action is defined on form, do nothing
        return;
      }

      var form_gadget = this,
        erp5_form,
        form_id = this.state.erp5_document._embedded._view.form_id,
        action = form_gadget.state.erp5_document._embedded._view._actions.put;

      return form_gadget.getDeclaredGadget("erp5_form")
        .push(function (gadget) {
          erp5_form = gadget;
          return erp5_form.checkValidity();
        })
        .push(function (validity) {
          if (validity) {
            return form_gadget.notifySubmitting()
              .push(function () {
                // try to send the form data over the network to jIO storage
                return erp5_form.getContent();
              })
              .push(function (data) {

                data[form_id.key] = form_id['default'];

                return form_gadget.jio_putAttachment(
                  form_gadget.state.jio_key,
                  action.href,
                  data
                );
              })
              // handle response from the server
              .push(function (result) {
                if (result.target.responseType === "blob") {
                  return jIO.util.readBlobAsText(result.target.response);
                }
                return {target: {result: result.target.response}};
              })
              .push(function (event) {
                var message;
                try {
                  message = JSON.parse(event.target.result).portal_status_message;
                } catch (ignore) {
                }
                return form_gadget.notifySubmitted({
                  "message": message,
                  "status": "success"
                });
              })
              .push(function () {
                return form_gadget.redirect({command: 'reload'});
              })
              .push(undefined, function (error) {
                if (error.target !== undefined) {
                  var error_text = 'Encountered an unknown error. Try to resubmit',
                    promise;
                  // improve error message if we can
                  if (error.target.status === 400) {
                    error_text = 'Input data has errors';
                  } else if (error.target.status === 403) {
                    error_text = 'You do not have the permissions to edit the object';
                  } else if (error.target.status === 0) {
                    // no/default=0 status means a network connection problem 
                    error_text = 'Document was not saved! Resubmit when you are online or the document accessible';
                  }
                  // display translated error_text to user
                  promise = form_gadget.notifySubmitted()
                    .push(function () {
                      return form_gadget.translate(error_text);
                    })
                    .push(function (message) {
                      return form_gadget.notifyChange({
                        'message': message + '.',
                        'status': 'error'
                      });
                    });

                  // if server validation of form data failed (indicated by response code 400)
                  // we parse out field errors and display them to the user
                  if (error.target.status === 400) {
                    promise
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
                  return promise;
                }
                // throwing an error is the last desperate option
                throw error;
              });
          }
        });

    }, false, true);

}(window, rJS, RSVP, calculatePageTitle, jIO));