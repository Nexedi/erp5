/*global window, rJS, CKEDITOR*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, CKEDITOR) {
  "use strict";

  rJS(window)
    .ready(function () {
      var gadget = this,
        textarea = gadget.element.querySelector('textarea');
      gadget.state.ckeditor = CKEDITOR.replace(
        textarea,
        {
          toolbar: [
            {
              name: 'clipboard',
              groups: [ 'clipboard', 'undo' ],
              items: [
                'PasteText', 'Undo', 'Redo'
              ]
            },
            {
              name: 'basicstyles',
              groups: [ 'basicstyles', 'cleanup' ],
              items: [ 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript',
                'Superscript', '-', 'RemoveFormat' ]
            },
            {
              name: 'paragraph',
              groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ],
              items: [
                'NumberedList', 'BulletedList',
              ]
            },
            { name: 'links', items: [ 'Link', 'Unlink', 'Anchor' ] },
            {
              name: 'insert',
              items: [
                'Image',
                'Table',
                'HorizontalRule',
                'SpecialChar', 'PageBreak'
              ]
            },
            {
              name: 'styles',
              items: ['Styles', 'Format', 'Font', 'FontSize' ]
            },
            { name: 'colors', items: [ 'TextColor', 'BGColor' ] },
            {
              name: 'tools',
              items: [
                'Maximize',
              ]
            },
            { name: 'about', items: [ 'About' ] }
          ],
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
    })
    .declareAcquiredMethod("submitContent", "triggerSubmit")
    .declareAcquiredMethod("notifyChange", 'notifyChange')

    .declareMethod('render', function (options) {
      return this.changeState({
        key: options.key || "text_content",
        data: options.value || ""
      });
    })

    .declareMethod('getContent', function () {
      var result = {};
      result[this.state.key] = this.state.ckeditor.getData();
      return result;
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.state.ckeditor.setData(gadget.state.data);
    });

}(rJS, CKEDITOR));