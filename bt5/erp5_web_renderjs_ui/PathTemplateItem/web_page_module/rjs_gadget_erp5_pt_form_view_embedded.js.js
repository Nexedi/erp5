/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)


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
        name: options.name,
        view: options.view,
        editable: options.editable,
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        erp5_form: options.erp5_form || {},
        new_content_action: false,
        delete_action: false,
        save_action: false
      };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var form_gadget = this;

      // render the erp5 form
      return form_gadget.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          var form_options = form_gadget.state.erp5_form;

          form_options.erp5_document = form_gadget.state.erp5_document;
          form_options.form_definition = form_gadget.state.form_definition;
          form_options.view = form_gadget.state.view;
          form_options.name = form_gadget.state.name;
          form_options.editable = form_gadget.state.editable;

          return erp5_form.render(form_options);
        });
    })

    .declareMethod('triggerSubmit', function getContent() {
      return;
    });

}(window, rJS));