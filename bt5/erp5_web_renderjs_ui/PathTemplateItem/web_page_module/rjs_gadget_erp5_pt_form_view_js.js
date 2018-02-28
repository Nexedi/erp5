/*global window, rJS, RSVP, calculatePageTitle, isEmpty */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle, isEmpty) {
  "use strict";

  /** Return true if `field` resembles non-empty and non-editable field. */
  function isNonEmptyNonEditableField(field) {
    if (field === undefined || field === null) {return false; }
    // ListBox and FormBox should always get a chance to render because they
    // can contain editable fields
    if (field.type === "ListBox") {return true; }
    if (field.type === "FormBox") {return true; }
    // hidden fields should not be obviously rendered
    if (field.hidden === 1) {return false; }
    // empty default value is bad and final decision
    return !isEmpty(field['default']);
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod('isDesktopMedia', 'isDesktopMedia')

    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('checkValidity', function () {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.checkValidity();
        });
    }, {mutex: 'changestate'})
    .declareMethod('getContent', function () {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.getContent();
        });
    }, {mutex: 'changestate'})
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var state_dict = {
        jio_key: options.jio_key,
        title: options.title,
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
        .push(function (embedded_form_gadget) {
          var form_options = gadget.state.erp5_form,
            embedded_form = gadget.state.erp5_document._embedded._view,
            rendered_form = {},
            key, field;

          /* Remove empty non-editable fields to prevent them from displaying (business requirement).
             Deleting objects inplace was not a good idea.
             So we pass through only non-empty (non-editable) fields.
          */
          for (key in embedded_form) {
            if (key[0] !== "_" && embedded_form.hasOwnProperty(key)) {
              if (isNonEmptyNonEditableField(embedded_form[key])) {
                rendered_form[key] = embedded_form[key];
              }
            }
          }
          form_options.erp5_document = {
            "_embedded": {
              "_view": rendered_form
            }
          };
          form_options.form_definition = gadget.state.form_definition;
          form_options.view = gadget.state.view;
          form_options.title = gadget.state.title;
          form_options.jio_key = gadget.state.jio_key;
          form_options.editable = 0; // because for editable=1 there is a special
                                     // page template 'pt_form_editable'. Once it is
                                     // is removed, this 0 should turn into gadget.state.editable
          return embedded_form_gadget.render(form_options);
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
            (gadget.state.erp5_document._links.action_object_jio_report ||
             gadget.state.erp5_document._links.action_object_jio_exchange ||
             gadget.state.erp5_document._links.action_object_jio_print) ?
              gadget.getUrlFor({command: 'change', options: {page: "export"}}) :
              "",
            calculatePageTitle(gadget, gadget.state.erp5_document),
            gadget.isDesktopMedia(),
            gadget.state.erp5_document._links.action_object_new_content_action ?
                gadget.getUrlFor({command: 'change', options: {
                  view: gadget.state.erp5_document._links.action_object_new_content_action.href,
                  editable: true
                }}) :
                ""
          ]);
        })
        .push(function (all_result) {
          var options = {
            edit_url: all_result[0],
            actions_url: all_result[1],
            selection_url: all_result[2],
            previous_url: all_result[3],
            next_url: all_result[4],
            tab_url: all_result[5],
            export_url: all_result[6],
            page_title: all_result[7]
          },
            is_desktop = all_result[8];
          if (is_desktop) {
            options.add_url = all_result[9];
          }
          return gadget.updateHeader(options);
        });
    });

}(window, rJS, RSVP, calculatePageTitle, isEmpty));