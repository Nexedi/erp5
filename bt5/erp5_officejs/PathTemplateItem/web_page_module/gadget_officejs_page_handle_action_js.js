/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP) {
  "use strict";

  var gadget_utils, action_reference, action_type;

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
      var gadget = this,
        child_gadget_url = 'gadget_erp5_pt_form_view_editable.html',
        parent_portal_type, action_code;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter("action"),
            gadget.getUrlParameter("action_type"),
            gadget.getUrlParameter("parent_portal_type"),
            gadget.getSetting('parent_portal_type'),
            gadget.declareGadget("gadget_officejs_common_utils.html")
          ]);
        })
        .push(function (result) {
          action_reference = result[0];
          action_type = result[1];
          parent_portal_type = result[2] || result[3];
          gadget_utils = result[4];
          return gadget_utils.getFormDefinition(parent_portal_type, action_reference)
            .push(function (form_definition) {
              if (action_type === "object_jio_js_script") {
                if (form_definition.fields_raw_properties.hasOwnProperty("gadget_field_action_js_script")) {
                  action_code = form_definition.fields_raw_properties.gadget_field_action_js_script.values.renderjs_extra[0];
                  return window.eval.call(window, '(function (gadget, gadget_utils, options,\
                                                    action_reference, parent_portal_type,\
                                                    form_definition, child_gadget_url, submit_code)\
                                                    {' + action_code[0] + '})')
                                                  (gadget, gadget_utils, options, action_reference, parent_portal_type, form_definition, child_gadget_url, action_code[1]);
                }
                else {
                  throw "Field 'gadget_field_action_js_script' missing in action \
                        form. Please check '" + action_reference + "' action configuration.";
                }
              } else {
                throw "Action type must be 'object_jio_js_script'. Please check \
                      '" + action_reference + "' action configuration.";
              }
            });
        });
    })

    .onStateChange(function () {
      return gadget_utils.renderGadget(this);
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
        content_dict = options[2],
        submit_code = gadget.state.submit_code;
      if (action_type === "object_jio_js_script") {
        return window.eval.call(window, '(function (gadget, gadget_utils, jio_key, content_dict)\
                                          {' + submit_code + '})')(gadget, gadget_utils, jio_key, content_dict);
      }
    });
}(document, window, rJS, RSVP));
