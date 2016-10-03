/*global window, rJS, RSVP, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle) {
  "use strict";

  rJS(window)

    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("displayFormulatorValidationError",
                           "displayFormulatorValidationError")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.element.querySelector('button').click();
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

    .declareMethod('updateDOM', function () {
      var form_gadget = this;

      // render the erp5 form
      return form_gadget.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          var form_options = form_gadget.state.erp5_form;

          form_options.erp5_document = form_gadget.state.erp5_document;
          form_options.form_definition = form_gadget.state.form_definition;
          form_options.view = form_gadget.state.view;

          return erp5_form.render(form_options);
        })

        // render the header
        .push(function () {
          var new_content_action = form_gadget.state.erp5_document._links.action_object_new_content_action,
            delete_action = form_gadget.state.erp5_document._links.action_object_delete_action,
            save_action = false;

          if (form_gadget.state.erp5_document._embedded._view._actions !== undefined) {
            if (form_gadget.state.erp5_document._embedded._view._actions.put !== undefined) {
              save_action = true;
            }
          }

          if (new_content_action !== undefined) {
            new_content_action = form_gadget.getUrlFor({command: 'change', options: {view: new_content_action.href, editable: true}});
          } else {
            new_content_action = "";
          }

          if (delete_action !== undefined) {
            delete_action = form_gadget.getUrlFor({command: 'change', options: {view: delete_action.href, editable: undefined}});
          } else {
            delete_action = "";
          }
          return RSVP.all([
            form_gadget.getUrlFor({command: 'change', options: {page: "tab"}}),
            form_gadget.getUrlFor({command: 'change', options: {page: "action", editable: true}}),
            new_content_action,
            form_gadget.getUrlFor({command: 'history_previous'}),
            delete_action,
            save_action,
            calculatePageTitle(form_gadget, form_gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          return form_gadget.updateHeader({
            tab_url: all_result[0],
            actions_url: all_result[1],
            add_url: all_result[2],
            selection_url: all_result[3],
            delete_url: all_result[4],
            cut_url: "",
            page_title: all_result[6],
            save_action: all_result[5]
          });
        });
    })

    .onEvent('submit', function () {
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
            return erp5_form.getContent()
              .push(function (data) {

                data[form_id.key] = form_id['default'];

                return RSVP.all([
                  form_gadget.notifySubmitting(),
                  form_gadget.jio_putAttachment(
                    form_gadget.state.id,
                    action.href,
                    data
                  )
                ]);
              })
              .push(form_gadget.notifySubmitted.bind(form_gadget))
              .push(function () {
                return form_gadget.redirect({command: 'reload'});
              })
              .push(undefined, function (error) {
                if ((error.target !== undefined) && (error.target.status === 400)) {
                  return form_gadget.notifySubmitted()
                    .push(function () {
                      return form_gadget.notifyChange();
                    })
                    .push(function () {
                      return form_gadget.displayFormulatorValidationError(JSON.parse(error.target.responseText));
                    });
                }
                throw error;
              });
          }
        });

    }, false, true);

}(window, rJS, RSVP, calculatePageTitle));