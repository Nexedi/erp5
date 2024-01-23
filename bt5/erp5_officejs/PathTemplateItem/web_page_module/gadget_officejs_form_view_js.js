/*global document, window, rJS, RSVP, Blob, URL, jIO, ensureArray, console, escape */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP, Blob, URL, jIO, ensureArray, console, escape) {
  "use strict";

  function renderField(field_id, field_definition, context_document,
                       data, blob_type, content_editable, gadget) {
    var key, raw_value, override, final_value, item_list, result = {}, i,
        extra_query, param_name, doc_key;
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
    if (result.renderjs_extra && blob_type) {
      result["default"] = data;
      result.editable = content_editable;
      if (!content_editable) {
        result.type = "EditorField";
      }
    }
    if (field_definition.type == "ListBox") {
      if (field_definition.values.default_params) {
        for (i = 0; i < field_definition.values.default_params.length; i += 1) {
          param_name = field_definition.values.default_params[i][0];
          doc_key = field_definition.values.default_params[i][1];
          if (context_document.hasOwnProperty(doc_key) &&
              context_document[doc_key]) {
            extra_query = ` AND ${param_name}:"${context_document[doc_key]}"`;
            result.query += escape(extra_query);
          }
        }
      }
    }
    if (field_definition.type == "GadgetField") {
      var context_dict = {}, renderjs_extra, rjs_extra_parsed;
      Object.assign(context_dict, gadget.state.doc);
      context_dict.jio_key = gadget.state.options.jio_key;
      if (field_definition.values.renderjs_extra &&
          !Array.isArray(field_definition.values.renderjs_extra)) {
        rjs_extra_parsed = JSON.parse(field_definition.values.renderjs_extra);
      }
      renderjs_extra = Object.assign({}, context_dict, rjs_extra_parsed);
      field_definition.values.renderjs_extra = JSON.stringify(renderjs_extra);
      result.renderjs_extra = JSON.stringify(renderjs_extra);
    }
    if (field_definition.values.extra) {
      eval(field_definition.values.extra);
    }
    if (field_definition.values.style_columns) {
      gadget.state.style_columns = field_definition.values.style_columns;
    }
    return result;
  }

  function renderForm(form_definition, context_document, data, blob_type,
                      content_editable, gadget) {
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
                                       context_document, data, blob_type,
                                       content_editable, gadget);
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

  function handleSubmit(gadget, child_gadget, content_dict) {
    var data;
    return gadget.notifySubmitting()
      .push(function () {
        if (gadget.state.blob_type) {
          //submit doc metadata
          data = content_dict.text_content;
          delete content_dict.text_content;
        }
        return child_gadget.submitContent(
          child_gadget.state.jio_key,
          undefined,
          content_dict
        );
      })
      .push(function () {
        if (gadget.state.blob_type) {
          //submit doc blob data
          return gadget
            .jio_putAttachment(child_gadget.state.jio_key, 'data',
                               jIO.util.dataURItoBlob(data));
        }
      }, function (error) {
        console.log(error);
        return gadget.notifySubmitted({
          message: "Submit failed",
          status: "error"
        });
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    // Format date rendering
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      if (gadget.state.style_columns &&
          gadget.state.style_columns[0][0] === 'jio_allDocs') {
        return new RSVP.Queue()
          .push(function () {
            return gadget.declareGadget(gadget.state.style_columns[0][1]);
          })
          .push(function (jio_alldocs) {
            return jio_alldocs.jio_allDocs(param_list, gadget);
          })
          .push(function (result) {
            if (result) {
              return result;
            } else {
              return gadget.jio_allDocs(param_list[0]);
            }
          });
      }
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          function truncate(str, n) {
            return (str.length > n) ? str.slice(0, n - 1) + '...' : str;
          }
          var i, date, len = result.data.total_rows, date_key_array;
          for (i = 0; i < len; i += 1) {
            // truncate long strings
            for (var key in result.data.rows[i].value) {
              result.data.rows[i].value[key] =
                truncate(result.data.rows[i].value[key], 100);
            }
            // render dates with proper format
            date_key_array = Object.keys(
              result.data.rows[i].value).filter((k) => k.includes("date") ||
                                                k.includes("Date"));
            date_key_array.forEach((date_key) => {
              if (result.data.rows[i].value.hasOwnProperty(date_key)) {
                date = new Date(result.data.rows[i].value[date_key]);
                result.data.rows[i].value[date_key] = {
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
                    key: "date",
                    required: 0,
                    timezone_style: 0,
                    title: "Date",
                    type: "DateTimeField"
                  }
                };
                result.data.rows[i].value["listbox_uid:list"] = {
                  key: "listbox_uid:list",
                  value: 2713
                };
              }
            });
            if (gadget.state.style_columns) {
              eval(gadget.state.style_columns[0][0]);
            }
          }
          return result;
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getContent", function (argument_list) {
      return this.getDeclaredGadget('erp5_pt_gadget')
        .push(function (child_gadget) {
          return child_gadget.getContent();
        });
    })

    .declareMethod("triggerSubmit", function (argument_list) {
      var gadget = this, child_gadget, content_dict;
      if (gadget.state.form_definition.portal_type_dict.custom_submit) {
        return gadget.declareGadget(gadget.state.form_definition
                                    .portal_type_dict.custom_submit)
          .push(function (submit_gadget) {
            return submit_gadget.handle_submit(argument_list, gadget.state);
          });
      }
      return gadget.getDeclaredGadget('erp5_pt_gadget')
        .push(function (result) {
          child_gadget = result;
          if (!child_gadget.state.editable) {
            return child_gadget.triggerSubmit(argument_list);
          }
          return child_gadget.getContent();
        })
        .push(function (result) {
          content_dict = result;
          if (!content_dict) { return; }
          return handleSubmit(gadget, child_gadget, content_dict);
        });
    }, {mutex: 'render'})

    .declareMethod("render", function (options) {
      var gadget = this,
        state_dict = {
          doc: options.doc,
          form_definition: options.form_definition,
          child_gadget_url: options.child_gadget_url,
          options: options
        },
        portal_type_dict = options.form_definition.portal_type_dict,
        blob;

      if (portal_type_dict.blob_type) {
        if (options.jio_key) {
          return gadget.jio_getAttachment(options.jio_key, "data")
            .push(undefined, function (error) {
              if (error.status_code === 404) {
                return new Blob([''], {type: portal_type_dict.blob_type});
              }
              throw new Error(error);
            })
            .push(function (result) {
              blob = result;
              blob.name = options.jio_key;
              return jIO.util.readBlobAsDataURL(blob);
            })
            .push(function (result) {
              if (portal_type_dict.blob_create_object_url) {
                state_dict.data = URL.createObjectURL(blob);
              } else {
                state_dict.data = {blob: result.target.result,
                                   name: options.jio_key};
              }
              state_dict.blob_type = portal_type_dict.blob_type;
              return gadget.changeState(state_dict);
            });
        }
      }
      return gadget.changeState(state_dict);
    }, {mutex: 'render'})

    .onStateChange(function onStateChange() {
      var fragment = document.createElement('div'),
        gadget = this,
        content_editable = gadget.state.content_editable,
        form_json;
      if (content_editable === undefined) {
        content_editable = gadget.state.form_definition
          .portal_type_dict.editable;
      }
      form_json = renderForm(gadget.state.form_definition, gadget.state.doc,
                               gadget.state.data, gadget.state.blob_type,
                               content_editable, gadget);
      while (gadget.element.firstChild) {
        gadget.element.removeChild(gadget.element.firstChild);
      }
      gadget.element.appendChild(fragment);
      return gadget.declareGadget(gadget.state.child_gadget_url,
                                      {element: fragment,
                                       scope: 'erp5_pt_gadget'})
        .push(function (form_gadget) {
          return gadget.renderSubGadget(gadget.state.options, form_gadget,
                                        form_json);
        });
    })

    .declareMethod("renderSubGadget", function (options, subgadget, form_json) {
      var gadget = this, erp5_document = form_json.erp5_document,
        portal_type_dict = form_json.form_definition.portal_type_dict,
        page_title = '', header_dict;
      if (options.doc && options.doc.title) {
        page_title = options.doc.title;
      } else if (options.doc && options.doc.header_title) {
        page_title = options.doc.header_title;
      }
      if (portal_type_dict.title) {
        page_title = portal_type_dict.title + page_title;
      }
      return subgadget.render({
        jio_key: options.jio_key,
        doc: options.doc,
        erp5_document: form_json.erp5_document,
        form_definition: form_json.form_definition,
        editable: portal_type_dict.editable,
        save_action: portal_type_dict.editable,
        view: options.view,
        form_json: form_json
      })
      // render the header
        .push(function () {
          var url_for_parameter_list = [
            {command: 'change', options: {page: "action_officejs",
                                          jio_key: options.jio_key,
                                          portal_type: options.portal_type}},
            {command: 'change', options: {page: "action_officejs",
                                          jio_key: options.jio_key,
                                          portal_type: options.portal_type}},
            {command: 'history_previous'},
            {command: 'selection_previous'},
            {command: 'selection_next'},
            {command: 'change', options: {page: "export"}},
            {command: 'display', options: {}},
            {command: 'change', options: {page: "create_document",
                                          jio_key: options.jio_key,
                                          portal_type:
                                          options.portal_type,
                                          new_content_dialog_form:
                                          form_json.form_definition
                                            .new_content_dialog_form,
                                          new_content_category:
                                          form_json.form_definition
                                            .new_content_category,
                                          allowed_sub_types_list:
                                          form_json.form_definition
                                            .allowed_sub_types_list
                                         }}
          ];
          erp5_document = form_json.erp5_document;
          return gadget.getUrlForList(url_for_parameter_list);
        })
        .push(function (url_list) {
          header_dict = { "page_title": page_title };
          if (options.form_type === 'dialog') {
            //TODO: find correct url
            header_dict.cancel_url = url_list[6];
          } else {
            header_dict.panel_action = portal_type_dict.panel_action === 1;
            if (portal_type_dict.filter_action) {
              header_dict.filter_action = true;
            }
            if (portal_type_dict.previous_next_button) {
              header_dict.previous_url = url_list[3];
              header_dict.next_url = url_list[4];
            }
            if (portal_type_dict.history_previous_link) {
              header_dict.selection_url = url_list[2];
            }
            if (portal_type_dict.has_more_views) {
              header_dict.tab_url = url_list[0];
            }
            if (portal_type_dict.editable === 1) {
              header_dict.save_action = true;
            }
            if (portal_type_dict.has_more_actions ||
                portal_type_dict.has_more_views) {
              header_dict.actions_url = url_list[1];
            }
            if (form_json.form_definition.allowed_sub_types_list &&
                form_json.form_definition.allowed_sub_types_list.length > 0 &&
                !portal_type_dict.hide_add_button) {
              header_dict.add_url = url_list[7];
            }
            if (portal_type_dict.export_button) {
              if (erp5_document._links.action_object_jio_report ||
                  erp5_document._links.action_object_jio_exchange ||
                  erp5_document._links.action_object_jio_print) {
                header_dict.export_url = url_list[5];
              }
            }
          }
          return gadget.declareGadget(portal_type_dict.custom_header);
        })
        .push(function (header_gadget) {
          return header_gadget.getOptions(portal_type_dict, options, header_dict);
        }, function (error) {
          if (!portal_type_dict.custom_header) {
            return header_dict;
          } else {
            throw error;
          }
        })
        .push(function (header_options) {
          return gadget.updateHeader(header_options);
        });
    });

}(document, window, rJS, RSVP, Blob, URL, jIO, ensureArray, console, escape));
