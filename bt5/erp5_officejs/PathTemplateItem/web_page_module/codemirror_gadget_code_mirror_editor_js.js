/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, CodeMirror, RSVP */
(function (window, rJS, CodeMirror, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("saveContent", "triggerSubmit")
    .declareMethod('render', function (options) {
      this.props.key = options.key || {};
      this.props.editor.setOption("mode", options.mode || "htmlmixed");
      this.props.editor.setValue(options.value || "");
    })

    .declareMethod('getContent', function () {
      var result = {};
      result[this.props.key || "text_content"] = this.props.editor.getValue();
      return result;
    })

    .declareService(function () {
      this.props.editor.refresh();
      this.props.editor.focus();
    })

    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          CodeMirror.commands.save = function () {
            return new RSVP.Queue()
              .push(function () {
                return g.saveContent();
              });
          };

          g.props.editor = CodeMirror.fromTextArea(g.props.element.querySelector("textarea"), {
            lineNumbers: true,
            styleActiveLine: true,
            showTrailingSpace: true,
            mode: "text/html",
            matchBrackets: true,
            tabSize: 2,
            indentWithTabs: false,
            showCursorWhenSelecting: true,
            continueComments: true,
            foldGutter: true,
            lineWrapping: true,
            gutters: ["CodeMirror-lint-markers",
                      "CodeMirror-linenumbers",
                      "CodeMirror-foldgutter"],
            lint: true,
            extraKeys: {
              "Ctrl-Space": "autocomplete",
              "Alt-Space": "autocomplete",
              "Ctrl-Q": function (cm) {cm.foldCode(cm.getCursor()); },
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
              'Alt-F': 'findPersistent',
              'Cmd-/': 'toggleComment',
              'Ctrl-/': 'toggleComment'
            }
          });
      // XXX custom styling for CribJS, should be put somewhere else-
          g.props.element.querySelector('.CodeMirror').setAttribute('style', 'min-height: 800px;');
        });

    });

}(window, rJS, CodeMirror, RSVP));