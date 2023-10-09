/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, JSONEditor, domsugar*/
(function (window, rJS, RSVP, document, JSONEditor, domsugar) {
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

      /* Overwrite some default implementation to follow up Nexedi features */
      JSONEditor.AbstractEditor.prototype.getDefault = function () {
        if (typeof this.schema.enum !== 'undefined') {
          this.schema.enum.unshift("");
          return "";
        }
        return undefined;
      }
      
      if (JSONEditor.defaults.editors.select.prototype.original_preBuild === undefined) {
        JSONEditor.defaults.editors.select.prototype.original_preBuild = JSONEditor.defaults.editors.select.prototype.preBuild
      }
      JSONEditor.defaults.editors.select.prototype.preBuild = function () {
        if (typeof this.schema.enum !== 'undefined') {
          this.schema.enum.unshift("");
        }
        this.original_preBuild()
      }

      JSONEditor.defaults.editors.select.prototype.getValue = function () {
        if (this.value === "") {
          return undefined
        }
        if (this.value === undefined) {
          return undefined
        }
        if (!this.dependenciesFulfilled) {
          return undefined
        }
        return this.typecast(this.value)
      }
      JSONEditor.defaults.editors.select.prototype.typecast = function(value) {
        if (this.schema.type === 'boolean') return value === 'undefined' || value === undefined ? undefined : !!value
        else if (this.schema.type === 'number' && value === "") return undefined
        else if (this.schema.type === 'integer' && value === "") return undefined
        else if (this.schema.type === 'number') return 1 * value || 0
        else if (this.schema.type === 'integer') return Math.floor(value * 1 || 0)
        else if (this.schema.enum && value === undefined) return undefined
        return `${value}`
      }

      /* The original code would remove the field if value is undefined */
      JSONEditor.defaults.editors.object.prototype.setValue = function(value, initial) {
        value = value || {}
    
        if (typeof value !== 'object' || Array.isArray(value)) value = {}                                                               
    
        /* First, set the values for all of the defined properties */
        Object.entries(this.cached_editors).forEach(([i, editor]) => {
          /* Value explicitly set */
          if (typeof value[i] !== 'undefined') {
            this.addObjectProperty(i)
            editor.setValue(value[i], initial)
            editor.activate()
          } else {
            editor.setValue(editor.getDefault(), initial)
          }
        })
    
        Object.entries(value).forEach(([i, val]) => {
          if (!this.cached_editors[i]) {
            this.addObjectProperty(i)
            if (this.editors[i]) this.editors[i].setValue(val, initial, !!this.editors[i].template)                                     
          }
        })
    
        this.refreshValue()
        this.layoutEditors()
        this.onChange()
      }
      /* End of patches related to ERP5 features */

      return new RSVP.Queue()
        .push(function () {
          return new JSONEditor(domsugar(jsonEditorContainer), {
            schema: gadget.state.json_field,
            ajax: true,
            theme: 'bootstrap5',
            show_errors: 'always',
            iconlib: 'fontawesome5',
            object_layout: 'normal',
            disable_collapse: true,
            disable_edit_json: true,
            disable_properties: true,
            keep_only_existing_values: false,
            use_default_values: false,		// important
            disable_array_reorder: true,
            disable_array_delete_all_rows: true,
            disable_array_delete_last_row: true,
            no_additional_properties: true,     // important
            remove_empty_properties: true,
            keep_oneof_values: false,		// important
            startval: gadget.state.default_dict
          });
        })
        .push(function (editor) {
          gadget.editor = editor;
          //editor.setValue(gadget.state.default_dict);
          return editor
        })
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
})(window, rJS, RSVP, document, JSONEditor, domsugar);