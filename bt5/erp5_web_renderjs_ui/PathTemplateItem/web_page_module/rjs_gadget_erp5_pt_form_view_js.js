/*global window, rJS, RSVP, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle) {
  "use strict";

  function isGoodNonEditableField(field) {
    // ListBox and FormBox should always get a chance to render
    if (field.type === "ListBox") {return true; }
    if (field.type === "FormBox") {return true; }
    // hidden fields should not be obviously rendered
    if (field.hidden === 1) {return false; }
    // field without default
    if (!field.default) {return false; }
    if (field.default.length === 0) {return false; }
    if (field.default.length === 1 && (!field.default[0])) {return false; }

    return true;
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('checkValidity', function () {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.checkValidity();
        });
    })
    .declareMethod('getContent', function () {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.getContent();
        });
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var state_dict = {
        jio_key: options.jio_key,
        view: options.view,
        editable: options.editable,
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        erp5_form: options.erp5_form || {}
      };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var gadget = this;

      // render the erp5 form
      return this.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          var form_options = gadget.state.erp5_form,
            rendered_form = gadget.state.erp5_document._embedded._view,
            key;

          // Remove all empty or otherwise bad non-editable fields
          for (key in rendered_form) {
            if (rendered_form.hasOwnProperty(key) && (key[0] !== "_")) {
              if (!isGoodNonEditableField(rendered_form[key])) {
                delete rendered_form[key];
              }
            }
          }

          form_options.erp5_document = gadget.state.erp5_document;
          form_options.form_definition = gadget.state.form_definition;
          form_options.view = gadget.state.view;
          form_options.jio_key = gadget.state.jio_key;
          form_options.editable = 0;

          return erp5_form.render(form_options);
        })

        // render the header
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'change', options: {editable: true}}),
            gadget.getUrlFor({command: 'change', options: {page: "action"}}),
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.getUrlFor({command: 'change', options: {page: "tab"}}),
            gadget.state.erp5_document._links.action_object_report_jio ?
                gadget.getUrlFor({command: 'change', options: {page: "export"}}) :
                "",
            calculatePageTitle(gadget, gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          return gadget.updateHeader({
            edit_url: all_result[0],
            actions_url: all_result[1],
            selection_url: all_result[2],
            previous_url: all_result[3],
            next_url: all_result[4],
            tab_url: all_result[5],
            export_url: all_result[6],
            page_title: all_result[7]
          });
        });
    });

}(window, rJS, RSVP, calculatePageTitle));