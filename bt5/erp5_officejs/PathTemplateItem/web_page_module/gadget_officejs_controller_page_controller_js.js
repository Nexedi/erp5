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
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getFormDefinition", function (portal_type) {
      var gadget = this,
        parent = "portal_types/" + portal_type,
        query = 'portal_type: "Action Information" AND reference: "jio_view" AND parent_relative_url: "' + parent + '"';
      return gadget.jio_allDocs({query: query})
        .push(function (data) {
          if (data.data.rows.length === 0) {
            throw "Can not find jio_view action for portal type " + portal_type;
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

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        jio_key = options[0],
        //target_url = options[1],
        content_dict = options[2];
      return gadget.notifySubmitting()
        .push(function () {
          // this should be jio_getattachment (using target_url)
          return gadget.jio_get(jio_key);
        })
        .push(function (document) {
          var property;
          for (property in content_dict) {
            if (content_dict.hasOwnProperty(property)) {
              document[property] = content_dict[property];
            }
          }
          return gadget.jio_put(jio_key, document);
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        child_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          if (document.portal_type === undefined) {
            throw new Error('Can not display document: ' + options.jio_key);
          }
          return gadget.getFormDefinition(document.portal_type)
            .push(function (form_definition) {
              return gadget.changeState({
                jio_key: options.jio_key,
                doc: document,
                child_gadget_url: child_gadget_url,
                form_definition: form_definition,
                editable: options.editable,
                view: options.view
              });
            });
        });
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

    .declareMethod("renderSubGadget", function (gadget, subgadget, form_json) {
      var erp5_document = form_json.erp5_document;
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
          {command: 'change', options: {page: "action"}},
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
          gadget.getUrlForList(url_for_parameter_list),
          gadget.isDesktopMedia(),
          gadget.getSetting('document_title_plural'),
          gadget.getSetting('upload_dict', false)
        ]);
      })
      .push(function (result_list) {
        var is_form_list = false, //TODO: configuration must indicate if is a form or list view
          url_list = result_list[0], header_dict;
        if (is_form_list) {
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
          if (false) { //TODO: configuration must indicate if there are more views
            header_dict.tab_url = url_list[0];
          }
          if (gadget.state.editable === "true") {
            header_dict.save_action = true;
          }
        }
        if (true) { //TODO: configuration must indicate if there are more actions
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
        return gadget.updateHeader(header_dict);
      });
    })

    .onStateChange(function () {
      var form_json, gadget = this,
        fragment = document.createElement('div');
      return gadget.renderForm(gadget.state.form_definition, gadget.state.doc)
        .push(function (json) {
          form_json = json;
          while (gadget.element.firstChild) {
            gadget.element.removeChild(gadget.element.firstChild);
          }
          gadget.element.appendChild(fragment);
          return gadget.declareGadget(gadget.state.child_gadget_url, {element: fragment, scope: 'fg'});
        })
        .push(function (form_gadget) {
          return gadget.renderSubGadget(gadget, form_gadget, form_json);
        });
    });

}(document, window, rJS, RSVP));