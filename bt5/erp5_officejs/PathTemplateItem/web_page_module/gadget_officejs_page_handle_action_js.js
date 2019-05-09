/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */

(function (window, document, rJS, RSVP) {
  "use strict";

  // TODO: move this to common utils
  function getFormInfo(form_definition) {
    var child_gadget_url,
      form_type,
      action_category = form_definition.action_type;
    switch (action_category) {
    case 'object_list':
      form_type = 'list';
      child_gadget_url = 'gadget_erp5_pt_form_list.html';
      break;
    case 'object_dialog':
      form_type = 'dialog';
      child_gadget_url = 'gadget_erp5_pt_form_dialog.html';
      break;
    case 'object_jio_js_script':
      form_type = 'dialog';
      child_gadget_url = 'gadget_erp5_pt_form_dialog.html';
      break;
    default:
      form_type = 'page';
      child_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
    }
    return [form_type, child_gadget_url];
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
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
      var gadget = this, action_reference, valid_action;
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
          valid_action = form_definition.action_type === "object_jio_js_script" &&
            form_definition.fields_raw_properties.hasOwnProperty("gadget_field_action_js_script");
          var fragment = document.createElement('div'),
            action_gadget_url = form_definition.fields_raw_properties.gadget_field_action_js_script.values.gadget_url,
            form_info = getFormInfo(form_definition),
            form_type = form_info[0],
            child_gadget_url = form_info[1];
          if (valid_action) {
            gadget.element.appendChild(fragment);
            return gadget.declareGadget(action_gadget_url, {
              scope: "action_field",
              element: fragment
            })
            .push(function (action_gadget) {
              return action_gadget.preRenderDocument(options);
            })
            .push(function (doc) {
              return gadget.changeState({
                doc: doc,
                parent_options: options,
                child_gadget_url: child_gadget_url,
                form_type: form_type,
                form_definition: form_definition,
                view: action_reference,
                valid_action: valid_action
              });
            });
          } else {
            //TODO refactor this to avoid 2 calls almost identical
            return gadget.changeState({
              doc: {},
              parent_options: options,
              child_gadget_url: child_gadget_url,
              form_type: form_type,
              form_definition: form_definition,
              view: action_reference,
              valid_action: valid_action
            });
          }
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this,
        options;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);
      return gadget.declareGadget("gadget_officejs_form_view.html", {element: fragment,
                                                                     scope: 'fg'})
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
        action_gadget_url, jio_key;
      if (gadget.state.valid_action) {
        action_gadget_url = gadget.state.form_definition.fields_raw_properties.gadget_field_action_js_script.values.gadget_url;
        gadget.element.appendChild(fragment);
        return gadget.declareGadget(action_gadget_url, {
          scope: "action_field",
          element: fragment
        })
        .push(function (action_gadget) {
          return action_gadget.handleSubmit(content_dict, gadget.state);
        })
        .push(function (id) {
          jio_key = id;
          return gadget.notifySubmitting();
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        })
        .push(function () {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: jio_key,
              editable: true
            }
          });
        });
      } else {
        return gadget.notifySubmitted({message: 'Could not perform this action: configuration error', status: 'fail'})
        .push(function () {
          return;
        });
      }
    });

}(window, document, rJS, RSVP));
