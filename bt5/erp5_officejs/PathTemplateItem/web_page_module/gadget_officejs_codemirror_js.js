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
            mode: "text/html",
            matchBrackets: true,
            showCursorWhenSelecting: true,
            extraKeys: {"Alt-F": "findPersistent"}
          });
      // XXX custom styling for CribJS, should be put somewhere else-
          g.props.element.querySelector('.CodeMirror').setAttribute('style', 'min-height: 800px;');
        });

    });

}(window, rJS, CodeMirror, RSVP));