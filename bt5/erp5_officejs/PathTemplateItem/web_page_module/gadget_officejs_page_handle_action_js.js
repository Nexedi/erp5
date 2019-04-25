/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
/*jslint evil: true */

(function (window, document, rJS, RSVP) {
  "use strict";

  var common_utils_gadget_url = "gadget_officejs_common_utils.html",
    gadget_utils,
    action_reference,
    action_type,
    action_gadget;

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

    .declareMethod("render", function (options) {
      var gadget = this, parent_portal_type, action_gadget_url;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter("action"),
            gadget.getUrlParameter("parent_portal_type"),
            gadget.getSetting('parent_portal_type'),
            gadget.declareGadget(common_utils_gadget_url)
          ]);
        })
        .push(function (result) {
          action_reference = result[0];
          parent_portal_type = result[1] || result[2];
          gadget_utils = result[3];
          return gadget_utils.getFormDefinition(parent_portal_type, action_reference)
            .push(function (form_definition) {
              action_type = form_definition.action_type;
              if (action_type === "object_jio_js_script") {
                if (form_definition.fields_raw_properties.hasOwnProperty("gadget_field_action_js_script")) {
                  action_gadget_url = form_definition.fields_raw_properties.gadget_field_action_js_script.values.gadget_url;
                  var fragment = document.createElement('div');
                  gadget.element.appendChild(fragment);
                  return gadget.declareGadget(action_gadget_url, {
                    scope: "action_field",
                    element: fragment
                  })
                    .push(function (declared_gadget) {
                      action_gadget = declared_gadget;
                      return action_gadget.handleRender(gadget, options, action_reference, form_definition);
                    });
                } else {
                  throw "Field 'gadget_field_action_js_script' missing in action form. Please check '" + action_reference + "' action configuration.";
                }
              } else {
                throw "Action type must be 'object_jio_js_script'. Please check '" + action_reference + "' action configuration.";
              }
            });
        });
    })

    .onStateChange(function () {
      return action_gadget.render(this);
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
      if (action_type === "object_jio_js_script") {
        action_gadget.handleSubmit(gadget, jio_key, content_dict);
      }
    });
}(window, document, rJS, RSVP));
