/*global document, window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP) {
  "use strict";

  function renderField(field_id, field_definition, document) {
    var result = {};
    for (var key in field_definition.values) {
      // order to get the final value (based on Field.py get_value)
      // 1.tales, 2.override, 3.form-def-value, 4.context-default
      var raw_value = field_definition.values[key],
        tales_expr = field_definition.tales[key],
        override = field_definition.overrides[key],
        final_value;
      final_value = undefined;
      if (tales_expr !== undefined && tales_expr !== null && tales_expr !== '') {
        try {
          throw "error";
          //final_value = eval(tales_expr);
        } catch (e) {} // TALES expressions are usually python code, so for now ignore
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
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
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
          return gadget.jio_get(data.data.rows[0].id)
            .push(function (action_result) {
              return gadget.jio_get(action_result.action)
                .push(function (form_result) {
                  return form_result.form_definition;
                });
            });
        });
    })

    .declareMethod("renderForm", function (form_definition, document) {
      var raw_properties = form_definition.fields_raw_properties;
      var form_json = {
        erp5_document: {
          "_embedded": {"_view": {}},
          "_links": {}
        },
        form_definition: form_definition
      }, i, j, fields, field_info, my_element, element_id;
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
            var rendered_field = renderField(element_id, field_info, document);
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
          return gadget.jio_get(jio_key)
            .push(function (document) {
              var property;
              for (property in content_dict) {
                if (content_dict.hasOwnProperty(property)) {
                  document[property] = content_dict[property];
                }
              }
              return gadget.jio_put(jio_key, document);
            });
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        child_gadget_url;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          if (document.portal_type !== undefined) {
            // use generic editable form view
            child_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
          } else {
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
      return subgadget.render({
        jio_key: gadget.state.jio_key,
        doc: gadget.state.doc,
        erp5_document: form_json.erp5_document,
        form_definition: form_json.form_definition,
        editable: gadget.state.editable,
        view: gadget.state.view,
        form_json: form_json
      })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (url_list) {
          return subgadget.updateHeader({
            page_title: gadget.state.doc.title,
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });
    })

    .onStateChange(function (modification_dict) {
      var fragment = document.createElement('div'),
        gadget = this;
      return gadget.renderForm(gadget.state.form_definition, gadget.state.doc)
        .push(function (form_json) {
          if (!modification_dict.hasOwnProperty('child_gadget_url')) {
            return gadget.getDeclaredGadget('fg')
              .push(function (child_gadget) {
                return gadget.renderSubGadget(gadget, child_gadget, form_json);
              });
          }
          // Clear first to DOM, append after to reduce flickering/manip
          while (gadget.element.firstChild) {
            gadget.element.removeChild(gadget.element.firstChild);
          }
          gadget.element.appendChild(fragment);
          return gadget.declareGadget(gadget.state.child_gadget_url, {element: fragment, scope: 'fg'})
            .push(function (form_gadget) {
              return gadget.renderSubGadget(gadget, form_gadget, form_json);
            });
        });
    });

}(document, window, rJS, RSVP));