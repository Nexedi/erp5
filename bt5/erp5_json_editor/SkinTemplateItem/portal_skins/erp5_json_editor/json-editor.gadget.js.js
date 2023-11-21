/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, JSONEditor, domsugar */
(function (window, rJS, RSVP, JSONEditor, domsugar) {
  'use strict';

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState({
        schema_url: options.schema_url,
        json_field: options.json_field,
        default_dict: options.default_dict,
        editable: options.editable,
        // Force refresh in any case
        render_timestamp: new Date().getTime()
      });
    })

    .onStateChange(function () {
      var gadget = this,
        jsonEditorContainer = gadget.element.querySelector('.json-editor-container');

      JSONEditor.AbstractEditor.prototype.getDefault = function () {
        /* Append an empty value and never load the default value on the field */
        if (this.schema.enum !== undefined) {
          this.schema.enum.unshift("");
          return "";
        }
        return undefined;
      };

      function isEmpty(obj) {
        return obj === undefined || obj === '' ||
          (
            obj === Object(obj) &&
            Object.keys(obj).length === 0 &&
            (obj.constructor === Object || obj.constructor === Array)
          );
      }

      JSONEditor.defaults.editors.object.prototype.getValue = function () {
        if (!this.dependenciesFulfilled) {
          return undefined;
        }
        /* original code uses super.getValue() but we cannot use super here */
        var result = this.value;
        if (result && (this.jsoneditor.options.remove_empty_properties || this.options.remove_empty_properties)) {
          Object.keys(result).forEach(function (key) {
            if (isEmpty(result[key])) {
              delete result[key];
            }
          });
        }
        return result;
      };

      JSONEditor.AbstractEditor.prototype.preBuild = function () {
        if (this.jsoneditor.options.readonly) {
          this.schema.readOnly = this.jsoneditor.options.readonly;
        }
      };

      if (JSONEditor.defaults.editors.select.prototype.original_preBuild === undefined) {
        JSONEditor.defaults.editors.select.prototype.original_preBuild = JSONEditor.defaults.editors.select.prototype.preBuild;
      }

      JSONEditor.defaults.editors.select.prototype.preBuild = function () {
        if (this.jsoneditor.options.readonly) {
          this.schema.readOnly = this.jsoneditor.options.readonly;
        }
        if (this.schema.enum !== undefined) {
          this.schema.enum.unshift("");
        }
        this.original_preBuild();
        if (this.schema.type === 'boolean') {
          /* the original code on preBuild include an empty first value if the value
           is not required, but we always want the empty value */
          if (this.isRequired()) {
            this.enum_display.unshift(' ');
            this.enum_options.unshift('undefined');
            this.enum_values.unshift(undefined);
          }
        }
      };

      JSONEditor.defaults.editors.select.prototype.getValue = function () {
        if (this.value === "") {
          return undefined;
        }
        if (this.value === undefined) {
          return undefined;
        }
        if (!this.dependenciesFulfilled) {
          return undefined;
        }
        return this.typecast(this.value);
      };

      JSONEditor.defaults.editors.select.prototype.typecast = function (value) {
        if (this.schema.type === 'boolean') {
          return value === 'undefined' || value === undefined ? undefined : !!value;
        }
        if (this.schema.type === 'number' && value === "") {
          return undefined;
        }

        if (this.schema.type === 'integer' && value === "") {
          return undefined;
        }

        if (this.schema.type === 'number') {
          return parseFloat(value) || 0;
        }

        if (this.schema.type === 'integer') {
          return Math.floor(parseFloat(value) || 0);
        }

        if (this.schema.enum && value === undefined) {
          return undefined;
        }
        if (value === undefined) {
          return undefined;
        }

        return value.toString();
      };

      /* The original code would remove the field if value is undefined */
      JSONEditor.defaults.editors.object.prototype.setValue = function (value, initial) {
        var object_editor = this;
        value = value || {};

        if (typeof value !== 'object' || Array.isArray(value)) {
          value = {};
        }

        /* First, set the values for all of the defined properties */
        // @ts-ignore
        Object.entries(this.cached_editors).forEach(function ([i, editor]) {
          /* Value explicitly set */
          if (value[i] !== undefined) {
            object_editor.addObjectProperty(i);
            editor.setValue(value[i], initial);
            editor.activate();
            /* Otherwise if it is read only remove the field */
          } else if (editor.schema.readOnly) {
            object_editor.removeObjectProperty(i);
            /* Otherwise, set the value to the default */
          } else {
            editor.setValue(editor.getDefault(), initial);
          }
        });

        // @ts-ignore
        Object.entries(value).forEach(function ([i, val]) {
          if (!object_editor.cached_editors[i]) {
            object_editor.addObjectProperty(i);
            if (object_editor.editors[i]) {
              object_editor.editors[i].setValue(val, initial, !!object_editor.editors[i].template);
            }
          }
        });

        object_editor.refreshValue();
        object_editor.layoutEditors();
        object_editor.onChange();
      };

      JSONEditor.defaults.editors.string.prototype.setValueToInputField = function (value) {
        this.input.value = value === undefined ? '' : value;
        /* ERP5: Once you set the value to the input, you also 
           updates the field value, otherwise the getValue will miss the value */
        this.value = this.input.value;
      };

      /* Backward compatibility with the usage of textarea property 
        if converts into json-editor proper property */
      JSONEditor.defaults.editors.string.prototype.preBuild = function () {
        if ((this.schema.textarea === true) || (this.schema.textarea === 1)) {
          this.schema.format = 'textarea';
        }
        if (this.jsoneditor.options.readonly) {
          this.schema.readOnly = this.jsoneditor.options.readonly;
        }
      };

      /* End of patches related to ERP5 features */

      if (Object.keys(gadget.state.json_field).length === 0) {
        return domsugar(jsonEditorContainer);
      }

      return new RSVP.Queue()
        .push(function () {
          return new JSONEditor(domsugar(jsonEditorContainer), {
            schema: gadget.state.json_field,
            ajax: true,
            theme: 'bootstrap5',
            show_errors: 'always',
            iconlib: 'fontawesome5',
            object_layout: 'normal',
            disable_collapse: false,
            disable_edit_json: true,
            disable_properties: false,
            keep_only_existing_values: false,
            use_default_values: false,
            disable_array_reorder: true,
            disable_array_delete_all_rows: true,
            disable_array_delete_last_row: true,
            no_additional_properties: false,
            remove_empty_properties: true,
            keep_oneof_values: false,
            startval: gadget.state.default_dict,
            readonly: gadget.state.editable ? false : true
          });
        })
        .push(function (editor) {
          gadget.editor = editor;
          return editor;
        });
    })
    .declareMethod(
      'getContent',
      function () {
        if (this.editor === undefined) {
          return {};
        }
        return this.editor.getValue();
      },
      { mutex: 'changestate' }
    )
    .declareMethod('checkValidity', function () {
      if (this.state.errors !== undefined) {
        return this.state.errors.length === 0;
      }
      return true;
    });
}(window, rJS, RSVP, JSONEditor, domsugar));