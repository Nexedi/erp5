/*jslint nomen: true, indent: 2 */
/*global window, rJS, CodeMirror*/
(function (window, rJS, CodeMirror) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .declareJob("deferNotifySubmit", function () {
      // Ensure error will be correctly handled
      return this.notifySubmit();
    })
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareJob("deferNotifyChange", function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })
    .ready(function () {
      var context = this;
      context.deferNotifyChangeBinded = context.deferNotifyChange.bind(context);
      this.editor = CodeMirror.fromTextArea(
        this.element.querySelector('textarea'),
        {
          // mode: mode,
          fullScreen: true,
          lineNumbers: true,
          styleActiveLine: true,
          showTrailingSpace: true,
          tabSize: 2,
          indentWithTabs: false,
          matchBrackets: true,
          matchTags: {bothTags: true},
          rulers: [{
            column: 80,
            color: "#bbb",
            lineStyle: "dashed"
          }],
          extraKeys: {
            "Ctrl-Space": "autocomplete",
            "Alt-Space": "autocomplete",
            "Ctrl-Q": function (cm) {
              cm.foldCode(cm.getCursor());
            },
            "Tab": function (cm) {
              // We want to insert spaces, not tab, and we also want to keep the behaviour of indenting selection.
              if (cm.getSelection()) {
                return cm.execCommand("defaultTab");
              }
              var spaces = new Array(cm.getOption("indentUnit") + 1).join(" ");
              cm.replaceSelection(spaces);
            },
            "Ctrl-I": "indentAuto",
            "Shift-Tab": "indentLess",
            "Ctrl-S": context.deferNotifySubmit.bind(context),
            "Ctrl-R": function () {
              // Disable page refresh to prevent data lose
              return;
            }
          },
          foldGutter: false,
          lineWrapping: true,
          gutters: ["CodeMirror-lint-markers",
                    "CodeMirror-linenumbers",
                    "CodeMirror-foldgutter"],
          lint: true
        }
      );
      this.editor.on('changes', this.deferNotifyChangeBinded);
    })

    .declareMethod('render', function (options) {
      var mode,
        state_dict = {
          key: options.key,
          editable: options.editable === undefined ? true : options.editable
        };
      if (options.portal_type === 'Web Page') {
        mode = 'htmlmixed';
      } else if (options.portal_type === 'Web Script') {
        mode = 'javascript';
      } else if (options.portal_type === 'Web Style') {
        mode = 'css';
      } else if ((options.portal_type === 'Python Script') ||
                 (options.portal_type === 'Test Component')) {
        mode = 'python';
      }
      state_dict.mode = mode;
      state_dict.value = options.value || "";
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('value')) {
        // Do not notify the UI when value is set
        this.editor.off('changes', this.deferNotifyChangeBinded);
        this.editor.setValue(this.state.value);
        this.editor.on('changes', this.deferNotifyChangeBinded);
      }
      if (modification_dict.hasOwnProperty('mode')) {
        this.editor.setOption("mode", this.state.mode);
      }
    })

    .declareMethod('getContent', function () {
      var form_data = {};
      if (this.state.editable) {
        form_data[this.state.key] = this.editor.getValue();
        // Change the value state in place
        // This will prevent the gadget to be changed if
        // its parent call render with the same value
        // (as ERP5 does in case of formulator error)
        this.state.value = form_data[this.state.key];
      }
      return form_data;
    });

}(window, rJS, CodeMirror));
