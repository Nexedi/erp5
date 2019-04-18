/*global window, rJS */
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
    .declareMethod("createDocument", function (options) {
      var gadget = this,
        doc = {
          title: "Untitled Document",
          portal_type: options.portal_type,
          parent_relative_url: options.parent_relative_url
        }, key, doc_key, doc_id;
      for (key in options) {
        if (options.hasOwnProperty(key)) {
          if (key.startsWith("my_")) {
            doc_key = key.replace("my_", "");
            doc[doc_key] = options[key];
          }
        }
      }
      return gadget.jio_post(doc);
    })

    .declareMethod("getFormDefinition", function (portal_type, action_reference) {
      var gadget = this,
        parent = "portal_types/" + portal_type,
        query = 'portal_type: "Action Information" AND reference: "' + action_reference + '" AND parent_relative_url: "' + parent + '"';
      return gadget.jio_allDocs({query: query})
        .push(function (data) {
          if (data.data.rows.length === 0) {
            throw "Can not find action '" + action_reference + "' for portal type '" + portal_type + "'";
          }
          return gadget.jio_get(data.data.rows[0].id);
        })
        .push(function (action_result) {
          return gadget.jio_get(action_result.action);
        })
        .push(function (form_result) {
          return form_result.form_definition;
        });
    })

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

    .declareMethod("renderGadget", function (target_gadget) {
      var fragment = document.createElement('div'),
        gadget = this, form_json;
      return gadget.renderForm(target_gadget.state.form_definition, target_gadget.state.doc)
        .push(function (json) {
          form_json = json;
          while (target_gadget.element.firstChild) {
            target_gadget.element.removeChild(target_gadget.element.firstChild);
          }
          target_gadget.element.appendChild(fragment);
          return target_gadget.declareGadget(target_gadget.state.child_gadget_url, {element: fragment, scope: 'fg'});
        })
        .push(function (form_gadget) {
          return gadget.renderSubGadget(target_gadget, form_gadget, form_json);
        });
    })

    .declareMethod("renderSubGadget", function (gadget, subgadget, form_json) {
      var this_gadget = this, erp5_document = form_json.erp5_document;
      return subgadget.render({
        jio_key: gadget.state.jio_key,
        doc: gadget.state.doc,
        erp5_document: form_json.erp5_document,
        form_definition: form_json.form_definition,
        editable: gadget.state.editable,
        view: gadget.state.view,
        form_json: form_json
      })
      // render the header
        .push(function () {
          var url_for_parameter_list = [
            {command: 'change', options: {page: "tab"}},
            {command: 'change', options: {page: "action_offline", jio_key: gadget.state.jio_key}},
            {command: 'history_previous'},
            {command: 'selection_previous'},
            {command: 'selection_next'},
            {command: 'change', options: {page: "export"}},
            {command: 'display', options: {}}
          ];
          erp5_document = form_json.erp5_document;
          if (erp5_document._links && erp5_document._links.action_object_new_content_action) {
            url_for_parameter_list.push({command: 'change', options: erp5_document._links.action_object_new_content_action});
          }
          return RSVP.all([
            this_gadget.getUrlForList(url_for_parameter_list),
            this_gadget.isDesktopMedia(),
            this_gadget.getSetting('document_title_plural'),
            this_gadget.getSetting('upload_dict', false)
          ]);
        })
        .push(function (result_list) {
          var url_list = result_list[0], header_dict;
          if (gadget.state.is_form_list) {
            header_dict = {
              panel_action: true,
              jump_url: "",
              fast_input_url: "",
              front_url: url_list[6],
              filter_action: true,
              page_title: result_list[2]
            };
          } else {
            header_dict = {
              selection_url: url_list[2],
              previous_url: url_list[3],
              next_url: url_list[4],
              page_title: gadget.state.doc.title
            };
            if (gadget.state.has_more_views) {
              header_dict.tab_url = url_list[0];
            }
            if (gadget.state.editable) {
              header_dict.save_action = true;
            }
          }
          if (gadget.state.has_more_actions) {
            header_dict.actions_url = url_list[1];
          }
          if (url_list[7]) {
            header_dict.add_url = url_list[7];
          }
          if (result_list[1]) {
            header_dict.export_url = (
              erp5_document._links.action_object_jio_report ||
              erp5_document._links.action_object_jio_exchange ||
              erp5_document._links.action_object_jio_print
            ) ? url_list[5] : '';
          }
          return this_gadget.updateHeader(header_dict);
        });
    });

}(document, window, rJS, RSVP));
