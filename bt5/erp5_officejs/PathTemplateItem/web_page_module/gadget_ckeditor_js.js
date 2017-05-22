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
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("submitContent", "triggerSubmit")
    .declareMethod('render', function (options) {
      var config = options.config || {
        removeButtons: 'NewPage,Preview,Cut,Paste,Copy,PasteText,' +
          'PasteFromWord,Flash,Iframe,Form,Checkbox,Radio,TextField,' +
          'Textarea,Select,Button,ImageButton,HiddenField,Maximize',
        removePlugins: '',
        disableNativeSpellChecker: false,
        extraAllowedContent: "details section article"
      },
      textarea = this.props.element.querySelector('textarea');

      this.props.ckeditor = CKEDITOR.replace(
        textarea,
         config  
      );
      this.props.ckeditor.addCommand('saveRJS', {
        readOnly: 1,
        exec: function () {
          return g.submitContent();
        }
      });
      this.props.ckeditor.ui.addButton('Save', {
        label: "Save",
        command: 'saveRJS',
        toolbar: 'document,1'
      });
          

      this.props.ckeditor.on('instanceReady', function (event) {
        event.editor.execCommand('maximize');
      });
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