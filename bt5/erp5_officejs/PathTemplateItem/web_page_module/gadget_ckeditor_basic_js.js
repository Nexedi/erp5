/*global window, rJS*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      return this.getDeclaredGadget('editor')
        .push(function (editor) {
          editor.render({
            key: options.key || "text_content",
            data: options.value || "",
            configuration: {
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
                    'NumberedList', 'BulletedList'
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
                    'Maximize'
                  ]
                },
                { name: 'about', items: [ 'About' ] }
              ],
              removePlugins: '',
              disableNativeSpellChecker: false,
              extraAllowedContent: "details section article"
            }
          });
        });
    });
}(rJS));