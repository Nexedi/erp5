/*global window, document, rJS, RSVP, console */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */

(function (window, document, rJS, RSVP, console) {
  "use strict";

  function declareActionGadget(gadget, state_options) {
    var fragment = document.createElement('div');
    gadget.element.appendChild(fragment);
    return gadget.declareGadget(state_options.action_gadget_url, {
      scope: "action_field",
      element: fragment
    });
  }

  function submitAction(gadget, action_gadget, state_options, content_dict) {
    var submit_dict;
    //handleSubmit() may return dictionary entries with
    //notification messages or redirect options
    state_options.gadget = gadget;
    return action_gadget.handleSubmit(content_dict, state_options)
      .push(function (result) {
        submit_dict = result;
        if (submit_dict.notify) {
          return gadget.notifySubmitted(submit_dict.notify);
        }
      })
      .push(function () {
        if (submit_dict.redirect) {
          return gadget.redirect(submit_dict.redirect);
        }
      }, function (error) {
        if (!(error instanceof RSVP.CancellationError)) {
          console.log("Action error:", error);
          return gadget.notifySubmitted({
            message: "Action Failed",
            status: "error"
          });
        }
        throw error;
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")

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
      var gadget = this,
        action_reference,
        form_definition,
        state_options,
        action_gadget;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter('portal_type'),
            gadget.getUrlParameter('parent_relative_url'),
            gadget.getUrlParameter("action")
          ]);
        })
        .push(function (result) {
          if (result[0] !== undefined) {
            options.portal_type = result[0];
          }
          if (result[1] !== undefined) {
            options.parent_relative_url = result[1];
          }
          action_reference = result[2];
          return gadget.getActionFormDefinition(action_reference);
        })
        .push(function (result) {
          form_definition = result;
          var form_type = form_definition.form_type,
            child_gadget_url = form_definition.child_gadget_url,
            //action validity determined by gadget_field_action_js_script field
            valid_action = form_definition.fields_raw_properties
              .hasOwnProperty("gadget_field_action_js_script");
          if (!valid_action) {
            return gadget.notifySubmitted({
              message: 'Could not perform this action: configuration error',
              status: 'fail'
            })
            .push(function (result) {
              return gadget.redirect({
                'command': 'display'
              });
            });
          }
          state_options = {
            doc: {},
            action_options: options,
            child_gadget_url: child_gadget_url,
            form_type: form_type,
            form_definition: form_definition,
            view: action_reference,
            valid_action: valid_action,
            action_gadget_url: form_definition.fields_raw_properties
              .gadget_field_action_js_script.values.gadget_url
          };
          delete form_definition.fields_raw_properties
            .gadget_field_action_js_script;
          return declareActionGadget(gadget, state_options);
        })
        .push(function (result) {
          action_gadget = result;
          options.form_definition = form_definition;
          //preRenderDocument() may return a document dict with fields to be
          //rendered in the action form, or configurations like skip_action_form
          return action_gadget.preRenderDocument(options);
        })
        .push(function (doc) {
          if (doc.header_dict) {
            state_options.header_dict = doc.header_dict;
            delete doc.header_dict;
          }
          state_options.doc = doc;
          if (doc.skip_action_form) {
            delete state_options.doc.skip_action_form;
            return submitAction(gadget, action_gadget, state_options, {});
          }
          return gadget.changeState(state_options);
        });
    }, {mutex: 'render'})

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
        })
        .push(function () {
          if (gadget.state.header_dict) {
            return gadget.updateHeader(gadget.state.header_dict);
          }
        });
    })

    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (gadget) {
          return gadget.triggerSubmit();
        });
    }, {mutex: 'render'})

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        content_dict = options[2];
      if (gadget.state.valid_action) {
        return gadget.notifySubmitting()
          .push(function () {
            return declareActionGadget(gadget, gadget.state);
          })
          .push(function (action_gadget) {
            return submitAction(gadget, action_gadget,
                                gadget.state, content_dict);
          });
      }
      return gadget.notifySubmitted(
        {message: 'Could not perform this action: configuration error',
         status: 'fail'});
    });

}(window, document, rJS, RSVP, console));
