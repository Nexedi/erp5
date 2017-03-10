/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, URI, calculatePageTitle */
(function (window, rJS, RSVP, URI, calculatePageTitle) {
  "use strict";

  rJS(window)
    .setState({
      title: ""
    })
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
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("displayFormulatorValidationError",
                           "displayFormulatorValidationError")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.element.querySelector('input[type="submit"]').click();
    })

    .declareMethod('render', function (options) {
      var state_dict = {
        id: options.jio_key,
        view: options.view,
        editable: options.editable,
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        erp5_form: options.erp5_form || {}
      };

      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var form_gadget = this,
        icon,
        selector = form_gadget.element.querySelector("h3"),
        title,
        i,
        view_list = this.state.erp5_document._links.action_workflow || [];

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

      for (i = 0; i < view_list.length; i += 1) {
        if (view_list[i].href === this.state.view) {
          title = view_list[i].title;
        }
      }


      // Calculate the h3 properties
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            form_gadget.translate(form_gadget.state.form_definition.title),
            form_gadget.translate(title),
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

          // <span class="ui-icon ui-icon-custom ui-icon-random">&nbsp;</span>
          form_options.erp5_document = form_gadget.state.erp5_document;
          form_options.form_definition = form_gadget.state.form_definition;
          form_options.view = form_gadget.state.view;
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


    .onEvent('submit', function () {
      var form_gadget = this,
        action = this.state.erp5_document._embedded._view._actions.put,
        form_id = this.state.erp5_document._embedded._view.form_id,
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

          data[form_id.key] = form_id['default'];
          // XXX Hardcoded
          data.dialog_id = form_id['default'];
          data.dialog_method = action.action;
          //XXX hack for redirect, difined in form
          redirect_to_parent = content_dict.field_your_redirect_to_parent;
          for (key in content_dict) {
            if (content_dict.hasOwnProperty(key)) {
              data[key] = content_dict[key];
            }
          }

          return form_gadget.jio_putAttachment(
            form_gadget.state.id,
            action.href,
            data
          );

        })
        .push(function (evt) {
          var location = evt.target.getResponseHeader("X-Location"),
            jio_key,
            list = [],
            message;
          try {
            message = JSON.parse(evt.target.response).portal_status_message;
          } catch (ignore) {
          }
          list.push(form_gadget.notifySubmitted(message));

          if (redirect_to_parent) {
            list.push(form_gadget.redirect({command: 'history_previous'}));
          } else {
            if (location === undefined || location === null) {
              // No redirection, stay on the same document
              list.push(form_gadget.redirect({command: 'change', options: {view: "view", page: undefined, editable: form_gadget.state.editable}}));
            } else {
              jio_key = new URI(location).segment(2);
              if (form_gadget.state.id === jio_key) {
                // Do not update navigation history if dialog redirect to the same document
                list.push(form_gadget.redirect({command: 'change', options: {jio_key: jio_key, view: "view", page: undefined, editable: form_gadget.state.editable}}));
              } else {
                list.push(form_gadget.redirect({command: 'push_history', options: {jio_key: jio_key, editable: form_gadget.state.editable}}));
              }
            }
          }
          return RSVP.all(list);
        })
        .push(undefined, function (error) {
          if ((error.target !== undefined) && (error.target.status === 400)) {
            return form_gadget.notifySubmitted()
              .push(function () {
                return form_gadget.translate('Input data has errors');
              })
              .push(function (message) {
                return form_gadget.notifyChange(message + '.');
              })
              .push(function () {
                return form_gadget.displayFormulatorValidationError(JSON.parse(error.target.responseText));
              });
          }
          throw error;
        });

    }, false, true);


}(window, rJS, RSVP, URI, calculatePageTitle));