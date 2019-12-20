/*jslint nomen: true, indent: 2 */
/*global window, rJS, monaco, JSLINT */
(function(window, rJS, monaco) {
  'use strict';

  rJS(window)
    .declareAcquiredMethod('notifySubmit', 'notifySubmit')
    .declareJob('deferNotifySubmit', function() {
      // Ensure error will be correctly handled
      return this.notifySubmit();
    })
    .declareAcquiredMethod('notifyChange', 'notifyChange')
    .declareJob('deferNotifyChange', function() {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })
    .ready(function() {
      var context = this,
        editor;
      function deferNotifyChange() {
        if (!context.state.ignoredChangeDuringInitialization) {
          return context.deferNotifyChange();
        }
      }
      this.editor = editor = monaco.editor.create(
        this.element.querySelector('.monaco-container'),
        {
          /* because Alt+Click is LeftClick on ChromeOS */
          multiCursorModifier: 'ctrlCmd',
          automaticLayout: true,
          autoIndent: true
        }
      );
      editor.addAction({
        id: 'save',
        label: 'Save',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S],
        precondition: null,
        keybindingContext: null,
        contextMenuGroupId: 'navigation',
        contextMenuOrder: 1.5,
        run: context.deferNotifySubmit.bind(context)
      });

      editor.getModel().updateOptions({
        tabSize: 2,
        insertSpaces: true
      });
      editor.getModel().onDidChangeContent(deferNotifyChange);
    })

    .declareJob('runJsLint', function () {
      var context = this;
      return new RSVP.Queue()
        .push(function () { return RSVP.delay(500); })
        .push(function () {
          if (context.state.model_language === 'javascript') {
            JSLINT(context.editor.getValue(), {});
            monaco.editor.setModelMarkers(
              context.editor.getModel(),
              'jslint',
              JSLINT.data()
                .errors.filter(Boolean)
                .map(err => ({
                  startLineNumber: err.line,
                  startColumn: err.character,
                  message: err.reason,
                  severity: monaco.MarkerSeverity.Error,
                  source: 'jslint'
                }))
            );
          }
        });
    })
    .declareMethod('render', function(options) {
      var model_language,
        state_dict = {
          key: options.key,
          editable: options.editable === undefined ? true : options.editable
        };
      if (options.portal_type === 'Web Page' || options.content_type == 'text/html') {
        model_language = 'html';
      } else if (options.portal_type === 'Web Script') {
        model_language = 'javascript';
      } else if (options.portal_type === 'Web Style') {
        model_language = 'css';
      } else if (options.portal_type === 'Python Script') {
        model_language = 'python';
      }
      state_dict.model_language = model_language;
      state_dict.value = options.value || '';
      return this.changeState(state_dict);
    })

    .onStateChange(function(modification_dict) {
      var queue = new RSVP.Queue();
      if (modification_dict.hasOwnProperty('value')) {
        // Do not notify the UI when initializing the value
        this.state.ignoredChangeDuringInitialization = true;
        this.editor.setValue(this.state.value);
        this.state.ignoredChangeDuringInitialization = false;
      }
      if (modification_dict.hasOwnProperty('model_language')) {
        monaco.editor.setModelLanguage(
          this.editor.getModel(),
          this.state.model_language
        );

        if (this.state.model_language === 'html') {
          // XXX why do we need this while it set on model already ? is it bug in monaco ?
          monaco.languages.html.htmlDefaults.options.format.tabSize = 2;
          monaco.languages.html.htmlDefaults.options.format.insertSpaces = true;
        }
        if (this.state.model_language === 'javascript') {
          // prettier as a formatting provider
          monaco.languages.registerDocumentFormattingEditProvider(
            'javascript',
            {
              provideDocumentFormattingEdits(model, options, token) {
                const text = prettier.format(model.getValue(), {
                  parser: 'babylon',
                  plugins: [prettierPlugins.babylon],
                  // see http://json.schemastore.org/prettierrc for supported options.
                  singleQuote: true,
                  tabWidth: 2
                });

                return [
                  {
                    range: model.getFullModelRange(),
                    text
                  }
                ];
              }
            }
          );

          // lint with jslint
          this.editor.getModel().onDidChangeContent(this.runJsLint.bind(this));
          this.runJsLint();

          // lint with typescript compiler
          monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
            noSemanticValidation: false,
            noSyntaxValidation: false
          });

          monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
            target: monaco.languages.typescript.ScriptTarget.ES6,
            allowNonTsExtensions: true,
            checkJs: true,
            allowJs: true,
            module: monaco.languages.typescript.ModuleKind.UMD
          });

          // Type mapping for Nexedi libraries
          function addExtraLibrary(script_name, lib_name) {
            return fetch(script_name)
              .then(function(resp) {
                return resp.text();
              })
              .then(function(script_code) {
                monaco.languages.typescript.javascriptDefaults.addExtraLib(
                  script_code,
                  lib_name
                );
              });
          }
          queue
            .push(addExtraLibrary('./monaco-rsvp.d.ts', 'rsvp'))
            .push(addExtraLibrary('./monaco-renderjs.d.ts', 'renderjs'))
            .push(addExtraLibrary('./monaco-jio.d.ts', 'jio'));
        }
      }
      return queue;
    })

    .declareMethod('getContent', function() {
      var form_data = {};
      if (this.state.editable) {
        form_data[this.state.key] = this.editor.getValue();
        // Change the value state in place
        // This will prevent the gadget to be changed if
        // its parent call render with the same value
        // (as ERP5 does in case of formulator error)
        this.state.value = form_data[this.state.key];
      }
      return form_data;
    });
})(window, rJS, monaco);
