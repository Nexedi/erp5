/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, document, rJS, RSVP, calculatePageTitle, Handlebars,
         ensureArray */
(function (window, document, rJS, RSVP, calculatePageTitle, Handlebars,
           ensureArray) {
  "use strict";

  function checkValidity() {
    return this.getDeclaredGadget("erp5_form")
      .push(function (declared_gadget) {
        return declared_gadget.checkValidity();
      });
  }

  function getContent() {
    return this.getDeclaredGadget("erp5_form")
      .push(function (sub_gadget) {
        return sub_gadget.getContent();
      });
  }

  function submitDialog(param_list) {
    var gadget = this,
      is_updating = param_list[0],
      // If you want to handle the submitDialog manually,
      // you can pass a custom dialog_method.
      custom_dialog_method = param_list.length > 1 ? param_list[1] : null,
      button_container =
          gadget.element.querySelector('.dialog_button_container'),
      update_button = button_container.querySelector('button'),
      submit_input = button_container.querySelector('input');
    submit_input.disabled = true;
    if (update_button !== null) {
      update_button.disabled = true;
    }

    function enableButton() {
      submit_input.disabled = false;
      if (update_button !== null) {
        update_button.disabled = false;
      }
    }

    return checkValidity.apply(gadget)
      .push(function (is_valid) {
        if (!is_valid) {
          enableButton();
          return;
        }
        return getContent.apply(gadget)
          .push(function (content_dict) {
            var data = {},
              key;

            // create a copy of sub_data so we do not modify them in-place
            for (key in content_dict) {
              if (content_dict.hasOwnProperty(key)) {
                data[key] = content_dict[key];
              }
            }
            // ERP5 expects target Script name in dialog_method field
            data.dialog_method = custom_dialog_method || gadget.state.form_definition.action;
            // For Update Action - override the default value from "action"
            if (is_updating) {
              data.dialog_method = gadget.state.form_definition.update_action;
              data.update_method = gadget.state.form_definition.update_action;
            }

            return data;
          })
          .push(function (data) {
            return gadget.submitContent(
              gadget.state.jio_key,
              gadget.state.erp5_document._embedded._view._actions.put.href,  // most likely points to Base_callDialogMethod
              data
            );
          })
          .push(function (result) {  // success redirect handler
            var splitted_jio_key_list,
              splitted_current_jio_key_list,
              command,
              i;
            if (is_updating || !result.jio_key) {
              return;
            }
            if (gadget.state.redirect_to_parent) {
              return gadget.redirect({command: 'history_previous'});
            }
            if ((gadget.state.jio_key === result.jio_key) &&
                (!result.view)) {
              // don't update navigation history when not really redirecting
              return gadget.redirect({command: 'cancel_dialog_with_history'});
            } else if (gadget.state.jio_key === result.jio_key) {
              command = 'display_with_history_and_cancel';
            } else {
              // Check if the redirection goes to a same parent's subdocument.
              // In this case, do not add current document to the history
              // example: when cloning, do not keep the original document in history
              splitted_jio_key_list = result.jio_key.split('/');
              splitted_current_jio_key_list = gadget.state.jio_key.split('/');
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
            }

            console.log('lets redirect', command, result.jio_key, result.view);
            // forced document change thus we update history
            return gadget.redirect({
              command: command,
              options: {
                "jio_key": result.jio_key,
                "view": result.view
                // do not mingle with editable because it isn't necessary
              }
            });
          })
          .push(function (result) {
            enableButton();
            return result;
          });
      }, function (error) {
        enableButton();
        throw error;
      });
      // We do not handle submit failures because Page Form handles them well
      // If any error bubbles here we do not know what to do with it anyway
  }


  var gadget_klass = rJS(window),
    dialog_button_source = gadget_klass.__template_element
                         .getElementById("dialog-button-template")
                         .innerHTML,
    dialog_button_template = Handlebars.compile(dialog_button_source);

  gadget_klass
    .setState({
      'redirect_to_parent': false,  // set by a presence of special field
      'has_update_action': undefined  // default "submit" issue update in case of its presence
    })

    /////////////////////////////////////////////////////////////////
    // acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("submitContent", "submitContent")
    .allowPublicAcquisition("submitDialog", submitDialog)

    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('checkValidity', checkValidity, {mutex: 'changestate'})

    .declareMethod('getContent', getContent, {mutex: 'changestate'})

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function triggerSubmit() {
      this.element.querySelector('input[type="submit"]').click();
    }, {mutex: 'changestate'})

    .declareMethod('render', function render(options) {
      var gadget = this;
      // copy out wanted items from options and pass it to `changeState`
      return gadget.getUrlParameter('extended_search')
        .push(function (extended_search) {
          return gadget.changeState({
            jio_key: options.jio_key,
            view: options.view,
            // ignore options.editable because dialog is always editable
            erp5_document: options.erp5_document,
            form_definition: options.form_definition,
            erp5_form: options.erp5_form || {},
            // editable: true,  // ignore global editable state (be always editable)
            action_title: options.form_definition.action_title,
            has_update_action: Boolean(options.form_definition.update_action),
            update_action_title: options.form_definition.update_action_title,
            // pass extended_search from previous view in case any gadget is curious
            extended_search: extended_search,
            redirect_to_parent: options.erp5_document._embedded._view.field_your_redirect_to_parent !== undefined
          });
        });
    })

    // .declareMethod('submitDialog', submitDialog, {mutex: 'changestate'})

    .onStateChange(function onStateChange(modification_dict) {
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
          if (modification_dict.hasOwnProperty('has_update_action') ||
              modification_dict.hasOwnProperty('update_action_title')) {
            return form_gadget.translateHtml(dialog_button_template({
              show_update_button: form_gadget.state.has_update_action
            }))
              .push(function (html) {
                var div = document.createElement('div'),
                  dialog_button_container = form_gadget.element
                                   .querySelector('.dialog_button_container');
                div.innerHTML = html;
                if (form_gadget.state.has_update_action && form_gadget.state.update_action_title) {
                  div.querySelector('button[name="action_update"]')
                     .textContent = form_gadget.state.form_definition
                                                     .update_action_title;
                }
                while (dialog_button_container.firstChild) {
                  dialog_button_container.firstChild.remove();
                }
                dialog_button_container.innerHTML = div.innerHTML;
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
          var action_confirm = form_gadget.element.querySelector('input.dialogconfirm');
          if (form_gadget.state.action_title) {
            action_confirm.value = form_gadget.state.action_title;
          } else {
            action_confirm.value = translated_title_list[1];
          }

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
          // this might cause problems if the listbox in the dialog is not curious
          // about the previous search
          if (form_gadget.state.extended_search) {
            form_options.form_definition.extended_search = form_gadget.state.extended_search;
          }
          return erp5_form.render(form_options);
        })
        .push(function () {
          // Render the headers
          return RSVP.all([
            form_gadget.getUrlFor({command: 'cancel_dialog_with_history'}),
            calculatePageTitle(form_gadget, form_gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          form_gadget.element.querySelector('a.dialogcancel').href = all_result[0];
          form_gadget.enableButtonAsJob();
          return form_gadget.updateHeader({
            cancel_url: all_result[0],
            page_title: all_result[1]
          });
        });
    })

    .onEvent('submit', function submit() {
      if (this.state.has_update_action === true) {
        // default action on submit is update in case of its existence
        return submitDialog.apply(this, [true]);
      }
      return submitDialog.apply(this, [false]);
    }, false, true)

    .onEvent('click', function click(evt) {
      if (evt.target.name === "action_confirm") {
        evt.preventDefault();
        return submitDialog.apply(this, [false]);
      }
      if (evt.target.name === "action_update") {
        evt.preventDefault();
        return submitDialog.apply(this, [true]);
      }
    }, false, false)

    .declareJob('enableButtonAsJob', function enableButton() {
      // click event listener is now activated
      // Change the state of the gadget
      var gadget = this,
        button_container =
            gadget.element.querySelector('.dialog_button_container'),
        update_button = button_container.querySelector('button'),
        submit_input = button_container.querySelector('input');
      submit_input.disabled = false;
      if (update_button !== null) {
        update_button.disabled = false;
      }
    });

}(window, document, rJS, RSVP, calculatePageTitle, Handlebars, ensureArray));
