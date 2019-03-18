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

  function renderForm(form_definition, document) {
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
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod('isDesktopMedia', 'isDesktopMedia')
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getFormDefinition", function (portal_type) {
      var gadget = this,
          // TODO: task "Remove the hardcoded form name"
          form_path = 'portal_skins/erp5_officejs_jio_connector/' +
            portal_type.replace(/ /g, '') +
            '_viewAsJio';
      return gadget.jio_get(form_path)
        .push(function (result) {
          return result._embedded._view.my_form_definition["default"];
        });
    })

    .declareMethod("renderForm", function (form_definition, document) {
      return renderForm(form_definition, document);
    })

    .declareMethod('submitContent', function (options) {
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
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .declareMethod('triggerSubmit', function triggerSubmit() {
      this.element.querySelector('button').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        child_gadget_url;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          if (document.portal_type !== undefined) {
            /*child_gadget_url = 'gadget_officejs_jio_' +
              result.portal_type.replace(/ /g, '_').toLowerCase() +
              '_view.html';*/
            // [HARDCODED] force to use form view
            child_gadget_url = "gadget_erp5_form.html";
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

    .declareMethod("renderSubGadget", function (gadget, subgadget, form_json) {
      var render_options = {
        jio_key: gadget.state.jio_key,
        doc: gadget.state.doc,
        erp5_document: form_json.erp5_document,
        form_definition: form_json.form_definition,
        editable: gadget.state.editable,
        view: gadget.state.view,
        form_json: form_json,
        //new_content_action: false,
        //delete_action: false,
        save_action: false
      };
      if (form_json.erp5_document._embedded._view._actions !== undefined) {
        if (form_json.erp5_document._embedded._view._actions.put !== undefined) {
          render_options.save_action = true;
        }
      }
      return subgadget.render(render_options)
        .push(function () {
          var url_for_parameter_list = [
            {command: 'change', options: {page: "tab"}},
            {command: 'change', options: {page: "action"}},
            {command: 'history_previous'},
            {command: 'selection_previous'},
            {command: 'selection_next'},
            {command: 'change', options: {page: "export"}}
          ];
          if (form_json.erp5_document._links.action_object_new_content_action) {
            url_for_parameter_list.push({command: 'change', options: {
              view: form_json.erp5_document._links.action_object_new_content_action.href,
              editable: true
            }});
          }
          return RSVP.all([
            //calculatePageTitle(gadget, gadget.state.erp5_document),
            gadget.getUrlParameter('selection_index'), // check if needed
            gadget.getUrlForList(url_for_parameter_list),
            gadget.isDesktopMedia()
          ]);
        })
        .push(function (result_list) {
          var url_list = result_list[1],
            header_dict = {
              //tab_url: url_list[0],
              //actions_url: url_list[1],
              //add_url: url_list[6] || '',
              selection_url: url_list[2],
              previous_url: url_list[3],
              next_url: url_list[4],
              page_title: gadget.state.doc.title //or calculatePageTitle in RSVP.all ?
            };
          if (render_options.save_action === true) {
            header_dict.save_action = true;
          }
          if (result_list[2]) {
            header_dict.export_url = (
              form_json.erp5_document._links.action_object_jio_report ||
              form_json.erp5_document._links.action_object_jio_exchange ||
              form_json.erp5_document._links.action_object_jio_print
            ) ? url_list[5] : '';
          }
          return gadget.updateHeader(header_dict);
        });
    })

    .onStateChange(function (modification_dict) {
      var fragment = document.createElement('div'),
        gadget = this,
        submit_button = gadget.element.querySelector('button'),
        form = document.createElement('form');
      return gadget.renderForm(gadget.state.form_definition, gadget.state.doc)
        .push(function (form_json) {
          if (!modification_dict.hasOwnProperty('child_gadget_url')) {
            return gadget.getDeclaredGadget('sub_form')
              .push(function (child_gadget) {
                return gadget.renderSubGadget(gadget, child_gadget, form_json);
              });
          }
          // Clear first to DOM, append after to reduce flickering/manip
          while (gadget.element.firstChild) {
            gadget.element.removeChild(gadget.element.firstChild);
          }
          form.appendChild(fragment);
          form.appendChild(submit_button);
          gadget.element.appendChild(form);
          return gadget.declareGadget(gadget.state.child_gadget_url, {element: fragment, scope: 'sub_form'})
            .push(function (form_gadget) {
              return gadget.renderSubGadget(gadget, form_gadget, form_json);
            });
        });
    })

    .onEvent('submit', function submit() {
      var gadget = this;
      return gadget.getDeclaredGadget("sub_form")
        .push(function (form_gadget) {
          if (form_gadget.state.erp5_document._embedded._view._actions === undefined ||
              form_gadget.state.erp5_document._embedded._view._actions.put === undefined) {
            return;
          }
          var action = form_gadget.state.erp5_document._embedded._view._actions.put;
          return form_gadget.checkValidity()
            .push(function (is_valid) {
              if (!is_valid) {
                return null;
              }
              return form_gadget.getContent();
            })
            .push(function (content_dict) {
              if (content_dict === null) {
                return;
              }
              return gadget.submitContent([
                gadget.state.jio_key,
                action.href,
                content_dict
              ]);
            })
          .push(function (jio_key) {
            if (jio_key) {
              // success redirect callback receives jio_key
              return gadget.redirect({command: 'reload'});
            }
          });
        });
    }, false, true);

}(document, window, rJS, RSVP));