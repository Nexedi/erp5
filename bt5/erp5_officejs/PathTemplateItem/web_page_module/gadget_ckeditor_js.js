/*global window, rJS, CKEDITOR*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, CKEDITOR) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("submitContent", "triggerSubmit")
    .declareAcquiredMethod("notifyChange", 'notifyChange')
    .declareMethod('render', function (options) {
      return this.changeState({
        key: options.key || "text_content",
        data: options.value || "",
        configuration: options.configuration || {}
      });
    })
    .declareMethod('getContent', function () {
      var result = {};
      result[this.state.key] = this.state.ckeditor.getData();
      return result;
    })
    .onStateChange(function (modification_dict) {
      var gadget = this, editor_id, editor,
        textarea = gadget.element.querySelector('textarea');
      if (gadget.state.ckeditor === undefined) {
        textarea = gadget.element.querySelector('textarea');
        gadget.state.ckeditor = CKEDITOR.replace(
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
        gadget.state.ckeditor.addCommand('saveRJS', {
          readOnly: 1,
          exec: function () {
            return gadget.submitContent();
          }
        });
        gadget.state.ckeditor.ui.addButton('Save', {
          label: "Save",
          command: 'saveRJS',
          toolbar: 'document,1'
        });
        gadget.state.ckeditor.on('instanceReady', function (event) {
          event.editor.execCommand('maximize');
        });
        gadget.state.ckeditor.on('change', gadget.notifyChange);
      }
      if (modification_dict.hasOwnProperty('configuration') !== {}) {
        editor_id = gadget.state.ckeditor.name;
        editor = CKEDITOR.instances[editor_id];
        if (editor) { editor.destroy(true); }
        gadget.state.ckeditor = CKEDITOR.replace(
          textarea,
          modification_dict.configuration
        );
        gadget.state.ckeditor.on('instanceReady', function (event) {
          event.editor.execCommand('maximize');
        });
      }
      return gadget.state.ckeditor.setData(gadget.state.data);
    });

}(rJS, CKEDITOR));