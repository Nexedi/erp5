/*global window, rJS, RSVP, loopEventListener, document, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener, calculatePageTitle) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
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
      this.props.element.querySelector('button').click();
    })
    .declareMethod('render', function (options) {
      var erp5_document = options.erp5_document,
        form_gadget = this,
        action_dict = erp5_document._embedded._view._actions;

      form_gadget.props.id = options.jio_key;
      form_gadget.props.view = options.view;
      form_gadget.props.form_id = erp5_document._embedded._view.form_id;

      if (action_dict !== undefined) {
        form_gadget.props.action = erp5_document._embedded._view._actions.put;
      }

      return form_gadget.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          var form_options = options.erp5_form || {},
            new_content_action,
            delete_action;

          form_options.erp5_document = options.erp5_document;
          form_options.form_definition = options.form_definition;
          form_options.view = options.view;

          new_content_action = options.erp5_document._links.action_object_new_content_action;
          if (new_content_action !== undefined) {
            new_content_action = form_gadget.getUrlFor({command: 'change', options: {view: new_content_action.href, editable: true}});
          } else {
            new_content_action = "";
          }


          delete_action = options.erp5_document._links.action_object_delete_action;
          if (delete_action !== undefined) {
            delete_action = form_gadget.getUrlFor({command: 'change', options: {view: delete_action.href, editable: undefined}});
          } else {
            delete_action = "";
          }
          return RSVP.all([
            erp5_form.render(form_options),
            form_gadget.getUrlFor({command: 'change', options: {page: "tab"}}),
            form_gadget.getUrlFor({command: 'change', options: {page: "action", editable: true}}),
            new_content_action,
            form_gadget.getUrlFor({command: 'history_previous'}),
            delete_action,
            calculatePageTitle(form_gadget, options.erp5_document)
          ]);
        })
        .push(function (all_result) {
          var header_dict = {
            tab_url: all_result[1],
            actions_url: all_result[2],
            add_url: all_result[3],
            selection_url: all_result[4],
            delete_url: all_result[5],
            cut_url: "",
            page_title: all_result[6]
          };
          if (form_gadget.props.action !== undefined) {
            header_dict.save_action = true;
          }

          return form_gadget.updateHeader(header_dict);
        });
    })


    .declareService(function () {
      ////////////////////////////////////
      // Form submit listening
      ////////////////////////////////////
      var form_gadget = this;

      function formSubmit() {
        var erp5_form;
        if (form_gadget.props.action === undefined) {
          // If not action is defined on form, do nothing
          return;
        }
        return form_gadget.getDeclaredGadget("erp5_form")
          .push(function (gadget) {
            erp5_form = gadget;
            return erp5_form.checkValidity();
          })
          .push(function (validity) {
            if (validity) {
              return erp5_form.getContent()
                .push(function (data) {

                  data[form_gadget.props.form_id.key] =
                                          form_gadget.props.form_id['default'];

                  return RSVP.all([
                    form_gadget.notifySubmitting(),
                    form_gadget.jio_putAttachment(
                      form_gadget.props.id,
                      form_gadget.props.action.href,
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
      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    });

}(window, rJS, RSVP, loopEventListener, calculatePageTitle));