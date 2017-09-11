/*jslint nomen: true, indent: 2 */
/*global window, rJS, CodeMirror*/
(function (window, rJS, CodeMirror) {
  "use strict";

  rJS(window)
    .ready(function () {
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
            "Shift-Tab": "indentLess"
            // "Ctrl-S": function(cm){saveDocument(cm, $.Event('click'))}
          },
          foldGutter: false,
          lineWrapping: true,
          gutters: ["CodeMirror-lint-markers",
                    "CodeMirror-linenumbers",
                    "CodeMirror-foldgutter"],
          lint: true
        }
      );
      window.editor = this.editor;
    })

    .declareMethod('render', function (options) {
      var mode;
      if (options.portal_type === 'Web Page') {
        mode = 'htmlmixed';
      } else if (options.portal_type === 'Web Script') {
        mode = 'javascript';
      } else if (options.portal_type === 'Web Style') {
        mode = 'css';
      }
      return this.changeState({
        key: options.key,
        value: options.value || "",
        editable: options.editable === undefined ? true : options.editable,
        mode: mode
      });
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('value')) {
        this.editor.setValue(this.state.value);
      }
      if (modification_dict.hasOwnProperty('mode')) {
        this.editor.setOption("mode", this.state.mode);
      }
    })

    .declareMethod('getContent', function () {
      var form_data = {};
      if (this.state.editable) {
        form_data[this.state.key] = this.editor.getValue();
      }
      return form_data;
    });

}(window, rJS, CodeMirror));
