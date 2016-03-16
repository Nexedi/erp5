/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, CodeMirror */
(function (window, rJS, CodeMirror) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('submitData', 'triggerSubmit')

    .ready(function (g) {
      g.props = {};
      g.options = null;

      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.editor = CodeMirror.fromTextArea(
            element.querySelector('textarea'),
            {
              lineNumbers: true,
              theme: 'zenburn',
              keyMap: 'vim',
              matchBrackets: true,
              showCursorWhenSelecting: true,
              tabSize: 4,
              indentUnit: 4,
              indentWithTabs: false,
              extraKeys: {
                "Alt-;": function (cm) {
                  cm.setOption("fullScreen", !cm.getOption("fullScreen"));
                }
              }
            }
          );
        });
    })
    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.editor.setValue(options.data || "");
      CodeMirror.commands.save = function () {
        gadget.submitData();
      };
      //console.log(gadget.props.element.querySelector('.editor'));

    })
    .declareMethod('getData', function () {
      return this.editor.getValue();
    })
    .declareService(function () {
      this.editor.refresh();
      this.editor.focus();
    });
}(window, rJS, CodeMirror));