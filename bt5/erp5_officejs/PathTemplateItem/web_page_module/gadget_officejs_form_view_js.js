/*global document, window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP) {
  "use strict";

  function renderField(field_id, field_definition, document) {
    var key, raw_value, tales_expr, override, final_value, result = {};
    for (key in field_definition.values) {
      if (field_definition.values.hasOwnProperty(key)) {
        // order to get the final value (based on Field.py get_value)
        // 1.tales, 2.override, 3.form-def-value, 4.context-default
        raw_value = field_definition.values[key];
        tales_expr = field_definition.tales[key];
        override = field_definition.overrides[key];
        final_value = undefined;
        if (tales_expr !== undefined && tales_expr !== null && tales_expr !== '') {
          try {
            throw "error";
            //final_value = eval(tales_expr);
          } catch (ignore) {} // TALES expressions are usually python code, so for now ignore
        }
        if (final_value === undefined) {
          if (override !== undefined && override !== null && override !== '') {
            final_value = override;
          } else if (raw_value !== undefined && raw_value !== null && raw_value !== '') {
            final_value = raw_value;
          } else if (document && document.hasOwnProperty(key)) {
            final_value = document[key];
          }
        }
        if (final_value !== undefined && final_value !== null && final_value !== '') {
          result[key] = final_value;
        }
      }
    }
    result.type = field_definition.type;
    result.key = field_id;
    if (document && document.hasOwnProperty(field_id)) {
      result["default"] = document[field_id];
    }
    return result;
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("renderForm", function (form_definition, document) {
      var i, j, fields, field_info, my_element, element_id, rendered_field,
        raw_properties = form_definition.fields_raw_properties,
        form_json = {
          erp5_document: {
            "_embedded": {"_view": {}},
            "_links": {}
          },
          form_definition: form_definition
        };
      for (i = 0; i < form_definition.group_list.length; i += 1) {
        fields = form_definition.group_list[i][1];
        for (j = 0; j < fields.length; j += 1) {
          my_element = fields[j][0];
          if (my_element.startsWith("my_")) {
            element_id = my_element.replace("my_", "");
          } else if (my_element.startsWith("your_")) {
            element_id = my_element.replace("your_", "");
          } else {
            element_id = my_element;
          }
          if (raw_properties.hasOwnProperty(my_element)) {
            field_info = raw_properties[my_element];
            rendered_field = renderField(element_id, field_info, document);
            form_json.erp5_document._embedded._view[my_element] = rendered_field;
          }
        }
      }
      form_json.erp5_document._embedded._view._actions = form_definition._actions;
      form_json.erp5_document._links = form_definition._links;
      return form_json;
    })

    .declareMethod("render", function (options) {
      var fragment = document.createElement('div'),
        gadget = this,
        form_json;
      return gadget.renderForm(options.form_definition, options.doc)
        .push(function (json) {
          form_json = json;
          while (gadget.element.firstChild) {
            gadget.element.removeChild(gadget.element.firstChild);
          }
          gadget.element.appendChild(fragment);
          return gadget.declareGadget(options.child_gadget_url, {element: fragment, scope: 'fg'});
        })
        .push(function (form_gadget) {
          return gadget.renderSubGadget(options, form_gadget, form_json);
        });
    })

    .declareMethod("renderSubGadget", function (options, subgadget, form_json) {
      var this_gadget = this, erp5_document = form_json.erp5_document,
          page_title = options.portal_type, add_url;
      return subgadget.render({
        jio_key: options.jio_key,
        doc: options.doc,
        erp5_document: form_json.erp5_document,
        form_definition: form_json.form_definition,
        editable: options.editable,
        view: options.view,
        form_json: form_json
      })
      // render the header
        .push(function () {
          var url_for_parameter_list = [
            {command: 'change', options: {page: "tab"}},
            {command: 'change', options: {page: "action_officejs", jio_key: options.jio_key, portal_type: options.portal_type}},
            {command: 'history_previous'},
            {command: 'selection_previous'},
            {command: 'selection_next'},
            {command: 'change', options: {page: "export"}},
            {command: 'display', options: {}}
          ];
          if (options.doc) {
            page_title = options.doc.title;
          }
          erp5_document = form_json.erp5_document;
          //add elements must be done via actions, so no 'add' button
          /*if (erp5_document._links && erp5_document._links.action_object_new_content_action) {
            url_for_parameter_list.push({command: 'change', options: erp5_document._links.action_object_new_content_action});
            add_url = true;
          }*/
          return RSVP.all([
            this_gadget.getUrlForList(url_for_parameter_list),
            this_gadget.isDesktopMedia(),
            this_gadget.getSetting('document_title_plural'),
            this_gadget.getSetting('upload_dict', false)
          ]);
        })
        .push(function (result_list) {
          var url_list = result_list[0], header_dict;
          if (options.form_type === 'dialog') {
            header_dict = {
              page_title: page_title,
              //TODO: find correct url
              cancel_url: url_list[6]
            };
          } else {
            if (options.form_type === 'list') {
              header_dict = {
                panel_action: true,
                jump_url: "",
                fast_input_url: "",
                filter_action: true,
                page_title: result_list[2]
              };
              if (!options.front_page) {
                header_dict.selection_url = url_list[2];
                header_dict.front_url = url_list[6];
              }
            } else {
              header_dict = {
                selection_url: url_list[2],
                previous_url: url_list[3],
                next_url: url_list[4],
                page_title: page_title
              };
              if (options.form_definition.has_more_views) {
                header_dict.tab_url = url_list[0];
              }
              if (options.editable) {
                header_dict.save_action = true;
              }
            }
            if (options.form_definition.has_more_actions) {
              header_dict.actions_url = url_list[1];
            }
            if (add_url) {
              header_dict.add_url = url_list[url_list.length - 1];
            }
            if (result_list[1]) {
              header_dict.export_url = (
                erp5_document._links.action_object_jio_report ||
                erp5_document._links.action_object_jio_exchange ||
                erp5_document._links.action_object_jio_print
              ) ? url_list[5] : '';
            }
          }
          return this_gadget.updateHeader(header_dict);
        });
    });

}(document, window, rJS, RSVP));
