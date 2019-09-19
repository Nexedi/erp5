/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */

(function (window, document, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getActionFormDefinition", function (action_reference) {
      var gadget = this, parent_portal_type;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter("parent_portal_type"),
            gadget.declareGadget("gadget_officejs_common_util.html")
          ]);
        })
        .push(function (result) {
          parent_portal_type = result[0];
          return result[1].getFormDefinition(parent_portal_type,
                                             action_reference);
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this, action_reference;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter('portal_type'),
            gadget.getUrlParameter('parent_relative_url'),
            gadget.getUrlParameter("action")
          ]);
        })
        .push(function (result) {
          if (result[0] !== undefined) { options.portal_type = result[0]; }
          if (result[1] !== undefined) {
            options.parent_relative_url = result[1];
          }
          action_reference = result[2];
          return gadget.getActionFormDefinition(action_reference);
        })
        .push(function (form_definition) {
          var fragment = document.createElement('div'),
            action_gadget_url,
            form_type = form_definition.form_type,
            child_gadget_url = form_definition.child_gadget_url,
            //an action form must have a GadgetField called
            //"gadget_field_new_action_js_script"
            //this gadget will point the custom action gadget
            valid_action = form_definition.action_type ===
              "object_jio_js_script" && form_definition.fields_raw_properties
              .hasOwnProperty("gadget_field_action_js_script"),
            state_options = {
              doc: {},
              action_options: options,
              child_gadget_url: child_gadget_url,
              form_type: form_type,
              form_definition: form_definition,
              view: action_reference,
              valid_action: valid_action
            };
          if (valid_action) {
            action_gadget_url = form_definition.fields_raw_properties
              .gadget_field_action_js_script.values.gadget_url;
            // as custom gadget render is being done here
            // avoid to child gadget to render it
            delete form_definition.fields_raw_properties
              .gadget_field_action_js_script;
            gadget.element.appendChild(fragment);
            return gadget.declareGadget(action_gadget_url, {
              scope: "action_field",
              element: fragment
            })
              .push(function (action_gadget) {
                options.form_definition = form_definition;
                return action_gadget.preRenderDocument(options);
              })
              .push(function (doc) {
                state_options.doc = doc;
                state_options.action_gadget_url = action_gadget_url;
                return gadget.changeState(state_options);
              }, function (error) {
                if (error.status === 404) {
                  return gadget.notifySubmitted({
                    message: "Error in action",
                    status: "error"
                  });
                }
                throw error;
              });
          }
          return gadget.changeState(state_options);
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);
      return gadget.declareGadget("gadget_officejs_form_view.html",
                                  {element: fragment, scope: 'fg'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        });
    })

    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (gadget) {
          return gadget.triggerSubmit();
        });
    })

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        //target_url = options[1],
        content_dict = options[2],
        fragment = document.createElement('div'),
        submit_dict;
      if (gadget.state.valid_action) {
        return gadget.notifySubmitting()
          .push(function () {
            gadget.element.appendChild(fragment);
            return gadget.declareGadget(gadget.state.action_gadget_url, {
              scope: "action_field",
              element: fragment
            });
          })
          .push(function (action_gadget) {
            return action_gadget.handleSubmit(content_dict, gadget.state);
          })
          .push(function (submit_result) {
            submit_dict = submit_result;
            //submit_dict must contain:
            //notify: options_dict for notifySubmitted
            //redirect: options_dict for redirect
            return gadget.notifySubmitted(submit_dict.notify);
          })
          .push(function () {
            return gadget.redirect(submit_dict.redirect);
          }, function (error) {
            if (!(error instanceof RSVP.CancellationError)) {
              return gadget.notifySubmitted({
                message: "Action Failed",
                status: "error"
              });
            }
            throw error;
          });
      }
      return gadget.notifySubmitted(
        {message: 'Could not perform this action: configuration error',
         status: 'fail'});
    });

}(window, document, rJS, RSVP));
