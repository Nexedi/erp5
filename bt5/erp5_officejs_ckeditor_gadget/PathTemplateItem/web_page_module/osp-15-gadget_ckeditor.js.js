/*global window, rJS, CKEDITOR*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, CKEDITOR) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          var textarea = element.querySelector('textarea');
          g.props.element = element;
          g.props.ckeditor = CKEDITOR.replace(
            textarea,
            {
              removeButtons: 'NewPage,Preview,Cut,Paste,Copy,PasteText,' +
                'PasteFromWord,Flash,Iframe,Form,Checkbox,Radio,TextField,' +
                'Textarea,Select,Button,ImageButton,HiddenField,Maximize',
              removePlugins: '',
              disableNativeSpellChecker: false,
              extraAllowedContent: "details section article"
            }
          );
          g.props.ckeditor.addCommand('saveRJS', {
            readOnly: 1,
            exec: function () {
              return g.submitContent();
            }
          });
          g.props.ckeditor.ui.addButton('Save', {
            label: "Save",
            command: 'saveRJS',
            toolbar: 'document,1'
          });
          g.props.ckeditor.on('instanceReady', function (event) {
            event.editor.execCommand('maximize');
          });
        });
    })
    .declareAcquiredMethod("submitContent", "triggerSubmit")
    .declareMethod('render', function (options) {
      this.props.key = options.key || "text_content";
      this.props.ckeditor.setData(options.value || "");
      return {};
    })

    .declareMethod('getContent', function () {
      var result = {};
      result[this.props.key] = this.props.ckeditor.getData();
      return result;
    });

}(rJS, CKEDITOR));