/*global document, window, rJS, RSVP, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP, ensureArray) {
  "use strict";

  function renderField(field_id, field_definition, context_document) {
    var key, raw_value, override, final_value, item_list, result = {};
    for (key in field_definition.values) {
      if (field_definition.values.hasOwnProperty(key)) {
        // order to get the final value (based on Field.py get_value)
        // 1.override, 2.form-def-value, 3.context-default
        raw_value = field_definition.values[key];
        override = field_definition.overrides[key];
        final_value = undefined;
        if (final_value === undefined) {
          if (override !== undefined && override !== null && override !== '') {
            final_value = override;
          } else if (raw_value !== undefined && raw_value !== null &&
                     raw_value !== '') {
            final_value = raw_value;
          } else if (context_document && context_document.hasOwnProperty(key)) {
            final_value = context_document[key];
          }
        }
        if (final_value !== undefined && final_value !== null &&
            final_value !== '') {
          result[key] = final_value;
        }
      }
    }
    result.type = field_definition.type;
    result.key = field_id;
    if (context_document && context_document.hasOwnProperty(field_id)) {
      if (field_definition.type === "ListField") {
        item_list = ensureArray(context_document[field_id])
          .map(function (item) {
            if (Array.isArray(item)) {return item; }
            return [item, item];
          });
        result.items = item_list;
      } else {
        result["default"] = context_document[field_id];
      }
    }
    return result;
  }

  function renderForm(form_definition, context_document) {
    var i, j, field_list, field_info, my_element, element_id, rendered_field,
      raw_properties = form_definition.fields_raw_properties,
      form_json = {
        erp5_document: {
          "_embedded": {"_view": {}},
          "_links": {}
        },
        form_definition: form_definition
      };
    for (i = 0; i < form_definition.group_list.length; i += 1) {
      field_list = form_definition.group_list[i][1];
      for (j = 0; j < field_list.length; j += 1) {
        my_element = field_list[j][0];
        if (my_element.startsWith("my_")) {
          element_id = my_element.replace("my_", "");
        } else if (my_element.startsWith("your_")) {
          element_id = my_element.replace("your_", "");
        } else {
          element_id = my_element;
        }
        if (element_id && raw_properties.hasOwnProperty(my_element)) {
          field_info = raw_properties[my_element];
          rendered_field = renderField(element_id, field_info,
                                       context_document);
          form_json.erp5_document._embedded._view[my_element] =
            rendered_field;
        }
      }
    }
    form_json.erp5_document._embedded._view._actions =
      form_definition._actions;
    form_json.erp5_document._links = form_definition._links;
    return form_json;
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    // XXX Hardcoded for modification_date rendering
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i, date, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("modification_date")) {
              date = new Date(result.data.rows[i].value.modification_date);
              result.data.rows[i].value.modification_date = {
                field_gadget_param: {
                  allow_empty_time: 0,
                  ampm_time_style: 0,
                  css_class: "date_field",
                  date_only: 0,
                  description: "The Date",
                  editable: 0,
                  hidden: 0,
                  hidden_day_is_last_day: 0,
                  "default": date.toUTCString(),
                  key: "modification_date",
                  required: 0,
                  timezone_style: 0,
                  title: "Modification Date",
                  type: "DateTimeField"
                }
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
          }
          return result;
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("triggerSubmit", function (argument_list) {
      return this.getDeclaredGadget('fg')
        .push(function (gadget) {
          if (gadget.state.save_action !== true) {
            //rely on child gadget to submit (filter, panels, etc.)
            return gadget.triggerSubmit(argument_list);
          }
          var action = gadget.state.erp5_document._embedded._view._actions.put;
          return gadget.getDeclaredGadget("erp5_form")
            .push(function (sub_gadget) {
              return sub_gadget.checkValidity();
            })
            .push(function (is_valid) {
              if (!is_valid) {
                return null;
              }
              return gadget.getContent();
            })
            .push(function (content_dict) {
              if (content_dict === null) {
                return;
              }
              return gadget.submitContent(
                gadget.state.jio_key,
                action.href,
                content_dict
              );
            }); // page form handles failures well enough
        });
    })

    .declareMethod("render", function (options) {
      var state_dict = {
        doc: options.doc,
        form_definition: options.form_definition,
        child_gadget_url: options.child_gadget_url,
        options: options
      };
      return this.changeState(state_dict);
    })

    .onStateChange(function onStateChange() {
      var fragment = document.createElement('div'),
        gadget = this,
        form_json = renderForm(gadget.state.form_definition, gadget.state.doc);
      while (gadget.element.firstChild) {
        gadget.element.removeChild(gadget.element.firstChild);
      }
      gadget.element.appendChild(fragment);
      return gadget.declareGadget(gadget.state.child_gadget_url,
                                      {element: fragment, scope: 'fg'})
        .push(function (form_gadget) {
          return gadget.renderSubGadget(gadget.state.options, form_gadget,
                                        form_json);
        });
    })

    .declareMethod("renderSubGadget", function (options, subgadget, form_json) {
      var this_gadget = this, erp5_document = form_json.erp5_document,
        page_title = options.portal_type,
        add_url = false;
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
            {command: 'change', options: {page: "action_officejs",
                                          jio_key: options.jio_key,
                                          portal_type: options.portal_type}},
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
          if (form_json.form_definition.allowed_sub_types_list &&
              form_json.form_definition.allowed_sub_types_list.length > 0 &&
              !form_json.form_definition.hide_add_button) {
            url_for_parameter_list.push({command: 'change',
                                         options: {page: "create_document",
                                                   jio_key: options.jio_key,
                                                   portal_type:
                                                   options.portal_type,
                                                   allowed_sub_types_list:
                                                   form_json.form_definition
                                                   .allowed_sub_types_list
                                                  }});
            add_url = true;
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
                //TODO which header links/buttons will be displayed
                //should be come from the configuration (form_definition)
                //jump_url: "",
                //fast_input_url: "",
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
              if (options.editable === true || options.editable === "true") {
                header_dict.save_action = true;
              }
            }
            if (options.form_definition.has_more_actions ||
                options.form_definition.has_more_views) {
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

}(document, window, rJS, RSVP, ensureArray));
