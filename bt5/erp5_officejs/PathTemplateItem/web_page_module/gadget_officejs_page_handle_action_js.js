/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */

(function (window, document, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getActionFormDefinition", function (action_reference) {
      var gadget = this, parent_portal_type;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter("parent_portal_type"),
            gadget.getSetting('parent_portal_type'),
            gadget.declareGadget("gadget_officejs_common_utils.html")
          ]);
        })
        .push(function (result) {
          parent_portal_type = result[0] || result[1];
          return result[2].getFormDefinition(parent_portal_type, action_reference);
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this, action_reference;
      return gadget.getUrlParameter("action")
        .push(function (action_parameter) {
          action_reference = action_parameter;
          return gadget.getActionFormDefinition(action_reference);
        })
        .push(function (form_definition) {
          if (form_definition.action_type === "object_jio_js_script") {
            if (form_definition.fields_raw_properties.hasOwnProperty("gadget_field_action_js_script")) {
              var fragment = document.createElement('div'),
                action_gadget_url = form_definition.fields_raw_properties.gadget_field_action_js_script.values.gadget_url;
              gadget.element.appendChild(fragment);
              return gadget.declareGadget(action_gadget_url, {
                scope: "action_field",
                element: fragment
              })
                .push(function (action_gadget) {
                  return action_gadget.handleRender(gadget, options, action_reference, form_definition);
                });
            }
          }
          // avoid crash if form doesn't have gadget_field_action_js_script or object_jio_js_script action
          // render form without submit (and warn/inform user?)
        });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getUrlParameter("action")
        .push(function (action_reference) {
          return gadget.getActionFormDefinition(action_reference);
        })
        .push(function (form_definition) {
          if (form_definition.fields_raw_properties.hasOwnProperty("gadget_field_action_js_script")) {
            var fragment = document.createElement('div'),
              action_gadget_url = form_definition.fields_raw_properties.gadget_field_action_js_script.values.gadget_url;
            gadget.element.appendChild(fragment);
            return gadget.declareGadget(action_gadget_url, {
              scope: "action_field",
              element: fragment
            })
              .push(function (action_gadget) {
                return action_gadget.render(gadget);
              });
          }
        });
    })

    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (gadget) {
          return gadget.triggerSubmit();
        });
    })

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        jio_key = options[0],
        //target_url = options[1],
        content_dict = options[2];
      return gadget.getUrlParameter("action")
        .push(function (action_reference) {
          return gadget.getActionFormDefinition(action_reference);
        })
        .push(function (form_definition) {
          if (form_definition.fields_raw_properties.hasOwnProperty("gadget_field_action_js_script")) {
            var fragment = document.createElement('div'),
              action_gadget_url = form_definition.fields_raw_properties.gadget_field_action_js_script.values.gadget_url;
            gadget.element.appendChild(fragment);
            return gadget.declareGadget(action_gadget_url, {
              scope: "action_field",
              element: fragment
            })
              .push(function (action_gadget) {
                return action_gadget.handleSubmit(gadget, jio_key, content_dict);
              });
          }
        });
    });
}(window, document, rJS, RSVP));
