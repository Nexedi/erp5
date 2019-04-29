/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */

(function (window, document, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

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
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter('portal_type'),
            gadget.getUrlParameter('parent_relative_url'),
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url'),
            gadget.getUrlParameter("action")
          ]);
        })
        .push(function (result) {
          action_reference = result[4];
          if (result[0] !== undefined) {options.portal_type = result[0]; } else {options.portal_type = result[2]; }
          if (result[1] !== undefined) {options.parent_relative_url = result[1]; } else {options.parent_relative_url = result[3]; }
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
                return action_gadget.render(options, action_reference, form_definition);
              });
            }
          }
          // avoid crash if form doesn't have gadget_field_action_js_script or object_jio_js_script action
          // render form without submit (and warn/inform user?)
        });
    })

    .declareMethod('triggerSubmit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('action_field')
        .push(function (action_gadget) {
          return action_gadget.triggerSubmit();
        });
    });

}(window, document, rJS, RSVP));
