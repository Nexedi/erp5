/*global window, document, rJS, CKEDITOR, RSVP*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, document, rJS, CKEDITOR, RSVP, loopEventListener) {
  "use strict";

  // http://nightly.ckeditor.com/17-10-11-06-04/full/samples/toolbarconfigurator/index.html#advanced
  var TOOLBAR_MOBILE = [
    {name: 'basicstyles', items: ['Bold', 'Italic', 'Underline']},
    {name: 'paragraph', items: ['NumberedList', 'BulletedList']},
    {name: 'links', items: ['Link']},
    {name: 'insert', items: ['Image']},
    {name: 'styles', items: ['Format']}
  ],
    TOOLBAR_DESKTOP = [
    {name: 'document',
     items: ['Source', '-', 'Save', 'Print', '-', 'Templates']},
    {name: 'clipboard', items: ['Undo', 'Redo']},
    {name: 'editing', items: ['Find', 'Replace', '-', 'SelectAll']},
    '/',
    {name: 'basicstyles',
     items: ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript',
             'Superscript', '-', 'RemoveFormat']},
    {name: 'paragraph',
     items: ['NumberedList', 'BulletedList', '-', 'Outdent',
             'Indent', '-', 'Blockquote', 'CreateDiv', '-',
             'JustifyLeft', 'JustifyCenter', 'JustifyRight',
             'JustifyBlock', '-', 'BidiLtr', 'BidiRtl', 'Language']},
    {name: 'links', items: ['Link', 'Unlink', 'Anchor']},
    {name: 'insert',
     items: ['Image', 'Table', 'HorizontalRule',
             'SpecialChar', 'PageBreak']},
    '/',
    {name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize']},
    {name: 'colors', items: ['TextColor', 'BGColor']},
    {name: 'tools', items: ['ShowBlocks']}
  ],
    MOBILE_CONFIGURATION = {
      toolbar: TOOLBAR_MOBILE,
      disableNativeSpellChecker: false,
      // Image pasting is already handled by a plugin
      clipboard_handleImages: false,
      // Remove the WebSpellChecker and SpellCheckAsYouType (SCAYT) plugins.
      removePlugins: 'scayt,wsc',
      // Disable ACF to not destroy HTML on mobile
      allowedContent: true,
      keystrokes: [
        [CKEDITOR.CTRL + 83, 'saveRJS']
      ]
    },
    DESKTOP_CONFIGURATION = {
      toolbar: TOOLBAR_DESKTOP,
      disableNativeSpellChecker: false,
      // Image pasting is already handled by a plugin
      clipboard_handleImages: false,
      // Remove the WebSpellChecker and SpellCheckAsYouType (SCAYT) plugins.
      removePlugins: 'scayt,wsc',
      // Disable ACF to not destroy HTML on mobile
      allowedContent: true,
      keystrokes: [
        [CKEDITOR.CTRL + 83, 'saveRJS']
      ]
    },
    READONLY_CONFIGURATION = {
      allowedContent: true,
      readOnly: true,
      clipboard_handleImages: false,
      // Remove the WebSpellChecker and SpellCheckAsYouType (SCAYT) plugins.
      removePlugins: 'elementspath,scayt,wsc,toolbar,pastefromword,' +
                     'tableselection,uploadwidget,clipboard,pastetext,' +
                     'widget,uploadimage,resize',
      startupShowBorders: false,
      startupOutlineBlocks: false,
      contentsCss: ''
    },
      MATCH_MEDIA = window.matchMedia("not screen and (min-width: 45em)");

  rJS(window)
    .declareAcquiredMethod("redirect", "redirect")
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

    .setState({
      is_mobile: false
    })

    .declareMethod('render', function (options) {
      this.listenToResize();
      return this.changeState({
        key: options.key,
        value: options.value || "",
        editable: options.editable === undefined ? true : options.editable,
        configuration: options.configuration || DESKTOP_CONFIGURATION,
        configuration_mobile: options.configuration_mobile ||
                              MOBILE_CONFIGURATION,
        configuration_readonly: options.configuration_readonly ||
                                READONLY_CONFIGURATION,
        is_responsive: (options.configuration_mobile !== undefined) ||
                       (options.configuration === undefined),
        is_mobile: MATCH_MEDIA.matches,
        language: options.language
      });
    })

    .declareMethod('getContent', function () {
      var result = {};
      if (this.state.editable) {
        result[this.state.key] = this.ckeditor.getData();
        // Change the value state in place
        // This will prevent the gadget to be changed if
        // its parent call render with the same value
        // (as ERP5 does in case of formulator error)
        this.state.value = result[this.state.key];
      }
      return result;
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        configuration;
      if (modification_dict.hasOwnProperty('configuration') ||
          modification_dict.hasOwnProperty('configuration_mobile') ||
          modification_dict.hasOwnProperty('configuration_readonly') ||
          modification_dict.hasOwnProperty('is_responsive') ||
          modification_dict.hasOwnProperty('is_mobile') ||
          modification_dict.hasOwnProperty('editable') ||
          modification_dict.hasOwnProperty('language')) {
        // Expected configuration changed.
        // Recreate ckeditor
        if (gadget.hasOwnProperty('ckeditor')) {
          // Destroy previous instance
          gadget.ckeditor.destroy();
        }
        // Create a new editor
        if (!gadget.state.editable) {
          configuration = gadget.state.configuration_readonly;
        } else if (gadget.state.is_responsive && gadget.state.is_mobile) {
          configuration = gadget.state.configuration_mobile;
        } else {
          configuration = gadget.state.configuration;
        }
        if (CKEDITOR.lang.languages[gadget.state.language] !== undefined) {
          configuration.language = gadget.state.language;
          configuration.defaultLanguage = gadget.state.language;
        }
        gadget.on_change_listener = gadget.deferNotifyChange.bind(gadget);
        gadget.ckeditor = CKEDITOR.replace(
          this.element.querySelector('textarea'),
          configuration
        );
        gadget.ckeditor.addCommand('saveRJS', {
          readOnly: 1,
          exec: gadget.deferNotifySubmit.bind(gadget)
        });
        gadget.ckeditor.ui.addButton('Save', {
          label: "Save",
          command: 'saveRJS',
          toolbar: 'document,1'
        });
        gadget.ckeditor.on('instanceReady', function (event) {
          event.editor.execCommand('maximize');
        });

        // Let CKEDITOR open inner links when in read-only mode
        gadget.ckeditor.on('contentDom', function () {
          var editable = gadget.ckeditor.editable();
          editable.attachListener(editable, 'click', function (event) {
            var link = new CKEDITOR.dom.elementPath(
              event.data.getTarget(), this).contains('a');
            if (link && event.data.$.button != 2 && link.isReadOnly()) {
              return gadget.redirect({
                'command': 'raw',
                'options': {
                  'url': link.getAttribute('href')
                }
              }, true);
            }
          }, null, null, 15);
        });
      }
      if (modification_dict.hasOwnProperty('value')) {
        // Prevent triggering notifyChange method when render is called
        // remove the change listener before calling setData and restore it after
        this.ckeditor.removeListener('change', this.on_change_listener);
        this.ckeditor.setData(this.state.value, {callback: function () {
          gadget.ckeditor.on('change', gadget.on_change_listener);
        }});
      }
    })

    .declareJob('listenToResize', function () {
      var result,
        event,
        context = this;
      function extractSizeAndDispatch() {
        if (MATCH_MEDIA.matches) {
          return context.changeState({
            is_mobile: true
          });
        }
        return context.changeState({
          is_mobile: false
        });
      }
      return loopEventListener(window, 'resize', false,
                               extractSizeAndDispatch);
    });


}(window, document, rJS, CKEDITOR, RSVP, rJS.loopEventListener));