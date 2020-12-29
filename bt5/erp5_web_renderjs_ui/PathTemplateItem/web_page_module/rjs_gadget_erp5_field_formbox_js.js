/*global window, rJS, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
/**
 * FormBox displays embedded form in itself.
 *
 * There are two common CSS classes bound to the FormBox Field
 * -  "horizontal_align_form_box" renders fields without labels in horizontal manner (useful for phone etc.)
 * -  "invisible" despite its name should only hide label
 *
 */
(function (window, rJS, URI) {
  "use strict";

  rJS(window)
    .setState({
      subgadget_template: undefined,
      editable: undefined
    })

    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod('render', function (options) {
      var gadget = this,
        field_json = options.field_json || {},
        new_state = {
          value: field_json.value || field_json['default'] || "",
          text_content: field_json.value || field_json['default'] || "",
          editable: field_json.editable,
          required: field_json.required,
          name: field_json.key,
          title: field_json.description,
          hidden: field_json.hidden,
          view: field_json.view,
          // field_json._embedded is HATEOASed subobj specs included in FormBox
          erp5_embedded_document: field_json._embedded
        };

      // prefer editability from the global context (form)
      if (options.editable !== undefined) {
        new_state.editable = options.editable;
      }

      return gadget.changeState(new_state);
    })

    .onStateChange(function () {
      var gadget = this,
        erp5_document_uri = new URI(gadget.state.erp5_embedded_document._view._links.traversed_document.href),
        form_options = {
          erp5_document: {
            _embedded: gadget.state.erp5_embedded_document
          },
          key: gadget.state.name,
          view: gadget.state.view,
          jio_key: erp5_document_uri.segment(2),
          editable: gadget.state.editable,
          embedded: true
        };

      // do not preserve objects in the state
      delete gadget.state.erp5_embedded_document;

      return gadget.getDeclaredGadget('sub')
        .push(function (subgadget) {
          return subgadget.render(form_options);
        });
    })

    .declareMethod('getContent', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.getContent();
          });
      }
      return {};
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.checkValidity();
          });
      }
      return true;
    }, {mutex: 'changestate'});

}(window, rJS, URI));