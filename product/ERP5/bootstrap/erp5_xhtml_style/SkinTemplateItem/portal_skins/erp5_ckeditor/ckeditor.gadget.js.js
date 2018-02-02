/*global window, document, rJS, CKEDITOR, RSVP*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, document, rJS, CKEDITOR, RSVP) {
  "use strict";

  // erp5_globals is not in xhtml_style.
  // Copy/Paste this function for now
  function loopEventListener(target, type, useCapture, callback,
                             prevent_default) {
    //////////////////////////
    // Infinite event listener (promise is never resolved)
    // eventListener is removed when promise is cancelled/rejected
    //////////////////////////
    var handle_event_callback,
      callback_promise;

    if (prevent_default === undefined) {
      prevent_default = true;
    }

    function cancelResolver() {
      if ((callback_promise !== undefined) &&
          (typeof callback_promise.cancel === "function")) {
        callback_promise.cancel();
      }
    }

    function canceller() {
      if (handle_event_callback !== undefined) {
        target.removeEventListener(type, handle_event_callback, useCapture);
      }
      cancelResolver();
    }
    function itsANonResolvableTrap(resolve, reject) {
      var result;
      handle_event_callback = function (evt) {
        if (prevent_default) {
          evt.stopPropagation();
          evt.preventDefault();
        }

        cancelResolver();

        try {
          result = callback(evt);
        } catch (e) {
          result = RSVP.reject(e);
        }

        callback_promise = result;
        new RSVP.Queue()
          .push(function () {
            return result;
          })
          .push(undefined, function (error) {
            if (!(error instanceof RSVP.CancellationError)) {
              canceller();
              reject(error);
            }
          });
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(itsANonResolvableTrap, canceller);
  }

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
    {name: 'editing', items: ['Find', 'Replace', '-', 'SelectAll',
                              '-', 'Scayt']},
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
     items: ['Image', 'Table', 'HorizontalRule', 'Smiley',
             'SpecialChar', 'PageBreak']},
    '/',
    {name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize']},
    {name: 'colors', items: ['TextColor', 'BGColor']},
    {name: 'tools', items: ['ShowBlocks']}
  ],
    MOBILE_CONFIGURATION = {
      toolbar: TOOLBAR_MOBILE,
      disableNativeSpellChecker: false,
      // Disable ACF to not destroy HTML on mobile
      allowedContent: true,
      keystrokes: [
        [CKEDITOR.CTRL + 83, 'saveRJS']
      ]
    },
    DESKTOP_CONFIGURATION = {
      toolbar: TOOLBAR_DESKTOP,
      disableNativeSpellChecker: false,
      // Disable ACF to not destroy HTML on mobile
      allowedContent: true,
      keystrokes: [
        [CKEDITOR.CTRL + 83, 'saveRJS']
      ]
    },
    READONLY_CONFIGURATION = {
      toolbar: [],
      allowedContent: true,
      readOnly: true,
      removePlugins: 'elementspath',
      startupShowBorders: false,
      startupOutlineBlocks: false,
      contentsCss: ''
    },
      MATCH_MEDIA = window.matchMedia("not screen and (min-width: 45em)");

  rJS(window)
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
        is_mobile: MATCH_MEDIA.matches
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
          modification_dict.hasOwnProperty('is_mobile')) {
        // Expected configuration changed.
        // Recreate ckeditor
        if (gadget.hasOwnProperty('ckeditor')) {
          // Destroy previous instance
          gadget.ckeditor.destroy();
        }
        // Create a new editor
        if (!modification_dict.editable) {
          configuration = gadget.state.configuration_readonly;
        } else if (gadget.state.is_responsive && gadget.state.is_mobile) {
          configuration = gadget.state.configuration_mobile;
        } else {
          configuration = gadget.state.configuration;
        }
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
        gadget.ckeditor.on('change', gadget.deferNotifyChange.bind(gadget));
      }
      if (modification_dict.hasOwnProperty('value')) {
        this.ckeditor.setData(this.state.value);
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


}(window, document, rJS, CKEDITOR, RSVP));