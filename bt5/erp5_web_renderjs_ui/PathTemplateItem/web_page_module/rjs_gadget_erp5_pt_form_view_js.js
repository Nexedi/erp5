/*global window, rJS, renderFormViewHeader, isEmpty,
         declareGadgetClassCanHandleListboxClipboardAction */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, renderFormViewHeader, isEmpty,
           declareGadgetClassCanHandleListboxClipboardAction) {
  "use strict";

  /** Return true if `field` resembles non-empty and non-editable field. */
  function isNonEmptyNonEditableField(field) {
    if (field === undefined || field === null) {return false; }
    // ListBox and FormBox should always get a chance to render because they
    // can contain editable fields
    if (field.type === "ListBox") {return true; }
    if (field.type === "FormBox") {return true; }
    // MatrixBox is often used for price tables or code tables. So it is always
    // useful for end users to display its contents.
    if (field.type === "MatrixBox") {return true; }
    // hidden fields should not be obviously rendered
    if (field.hidden === 1) {return false; }
    // empty default value must not be displayed
    if (isEmpty(field['default'])) {
      return false;
    }
    // relation field with no value must not be displayed too
    if ((field['default'].length === 1) && (isEmpty(field['default'][0]))) {
      return false;
    }
    // display the field by default
    return true;
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod('isDesktopMedia', 'isDesktopMedia')
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')

    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('checkValidity', function checkValidity() {
      return true;
    })
    .declareMethod('getContent', function getContent() {
      return {};
    })
    .declareMethod('triggerSubmit', function getContent() {
      return;
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function render(options) {
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

    .onStateChange(function onStateChange() {
      var gadget = this;

      // render the erp5 form
      return this.getDeclaredGadget("erp5_form")
        .push(function (embedded_form_gadget) {
          var form_options = gadget.state.erp5_form,
            embedded_form = gadget.state.erp5_document._embedded._view,
            rendered_form = {},
            key;

          /* Remove empty non-editable fields to prevent them from displaying (business requirement).
             Deleting objects inplace was not a good idea.
             So we pass through only non-empty (non-editable) fields.
          */
          for (key in embedded_form) {
            if (embedded_form.hasOwnProperty(key) && key[0] !== "_") {
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
          return renderFormViewHeader(gadget, gadget.state.jio_key,
                                      gadget.state.view,
                                      gadget.state.erp5_document);
        });
    });

  declareGadgetClassCanHandleListboxClipboardAction(rJS(window));

}(window, rJS, renderFormViewHeader, isEmpty,
  declareGadgetClassCanHandleListboxClipboardAction));