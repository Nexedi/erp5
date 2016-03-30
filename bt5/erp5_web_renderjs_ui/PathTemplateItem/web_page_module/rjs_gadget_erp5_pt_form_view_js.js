/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this;
      return this.getDeclaredGadget("erp5_form")
        .push(function (form_gadget) {
          var form_options = options.erp5_form || {},
            rendered_form = options.erp5_document._embedded._view,
            rendered_field,
            key;

          // Remove all empty fields, and mark all others as non editable
          for (key in rendered_form) {
            if (rendered_form.hasOwnProperty(key) && (key[0] !== "_")) {
              rendered_field = rendered_form[key];
              if ((rendered_field.type !== "ListBox") && ((!rendered_field.default) || (rendered_field.hidden === 1) || (rendered_field.default.length === 0))) {
                delete rendered_form[key];
              } else {
                rendered_field.editable = 0;
              }
            }
          }

          form_options.erp5_document = options.erp5_document;
          form_options.form_definition = options.form_definition;
          form_options.view = options.view;

          return RSVP.all([
            form_gadget.render(form_options),
            gadget.getUrlFor({command: 'change', options: {editable: true}}),
            gadget.getUrlFor({command: 'change', options: {page: "action"}}),
            gadget.getUrlFor({command: 'change', options: {page: "breadcrumb"}}),
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.getUrlFor({command: 'change', options: {page: "tab"}})
          ]);
        })
        .push(function (all_result) {

          return gadget.updateHeader({
            tab_url: all_result[7],
            actions_url: all_result[2],
            previous_url: all_result[5],
            next_url: all_result[6],
            export_url: "",
            edit_url: all_result[1],
            selection_url: all_result[4],
            page_title: options.erp5_document.title,
            breadcrumb_url: all_result[3]
          });
        });
    });

}(window, rJS, RSVP));