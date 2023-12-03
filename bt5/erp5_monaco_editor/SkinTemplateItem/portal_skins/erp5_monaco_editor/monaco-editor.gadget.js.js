/*jslint nomen: true, indent: 2 */
/*global window, rJS, monaco, JSLINT */
(function (window, rJS, monaco) {
  'use strict';

  // globals
  const JSLINT = window['JSLINT'];
  const prettier = window['prettier'];
  const prettierPlugins = window['prettierPlugins'];

  rJS(window)
    .declareAcquiredMethod('notifySubmit', 'notifySubmit')
    .declareJob('deferNotifySubmit', function () {
      // Ensure error will be correctly handled
      return this.notifySubmit();
    })
    .declareAcquiredMethod('notifyChange', 'notifyChange')
    .declareJob('deferNotifyChange', function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })
    .ready(function (context) {
      let editor;
      function deferNotifyChange() {
        if (!context.state.ignoredChangeDuringInitialization) {
          return context.deferNotifyChange();
        }
      }
      context.editor = editor = monaco.editor.create(
        this.element.querySelector('.monaco-container'),
        {
          autoIndent: true,
          automaticLayout: window.ResizeObserver ? true : false,
          stickyScroll: {
            enabled: true,
            maxLineCount: 3
          }
        }
      );

      editor.addAction({
        id: 'save',
        label: 'Save',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS],
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
        .push(function () {
          return RSVP.delay(500);
        })
        .push(function () {
          if (context.state.model_language === 'javascript') {
            JSLINT(context.editor.getValue(), {});
            monaco.editor.setModelMarkers(
              context.editor.getModel(),
              'jslint',
              JSLINT.data()
                .errors.filter(Boolean)
                .map((err) => ({
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
    .declareMethod('render', function (options) {
      var model_language,
        state_dict = {
          key: options.key,
          editable: options.editable === undefined ? true : options.editable
        };
      if (
        options.portal_type === 'Web Page' ||
        options.content_type == 'text/html'
      ) {
        model_language = 'html';
      } else if (options.portal_type === 'Web Script') {
        model_language = 'javascript';
      } else if (options.portal_type === 'Web Style') {
        model_language = 'css';
      } else if (options.portal_type === 'SQL Method') {
        model_language = 'sql';
      } else if (
        options.portal_type === 'Python Script' ||
        options.portal_type === 'Workflow Script' ||
        options.portal_type === 'Test Component' ||
        options.portal_type === 'Extension Component' ||
        options.portal_type === 'Document Component' ||
        options.portal_type === 'Tool Component' ||
        options.portal_type === 'Interface Component' ||
        options.portal_type === 'Mixin Component' ||
        options.portal_type === 'Module Component'
      ) {
        model_language = 'python';
      } else if (options.content_type === 'application/json') {
        model_language = 'json';
        state_dict.schema_url = options.schema_url;
      } else if (options.content_type === 'application/x-yaml') {
        model_language = 'yaml';
        state_dict.schema_url = options.schema_url;
      }
      state_dict.model_language = model_language;
      state_dict.value = options.value || '';
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var queue = new RSVP.Queue();
      // make the editor readonly until fully initialized
      this.editor.updateOptions({ readOnly: true });
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
                  parser: 'babel',
                  plugins: [prettierPlugins.babel],
                  // see http://json.schemastore.org/prettierrc for supported options.
                  singleQuote: true,
                  tabWidth: 2,
                  trailingComma: 'none'
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
            target: monaco.languages.typescript.ScriptTarget.Latest,
            allowNonTsExtensions: true,
            checkJs: true,
            allowJs: true,
            module: monaco.languages.typescript.ModuleKind.UMD
          });

          // Type mapping for Nexedi libraries
          const addExtraLibrary = function (script_name, lib_name) {
            return () => {
              return fetch(script_name)
                .then(function (resp) {
                  return resp.text();
                })
                .then(function (script_code) {
                  monaco.languages.typescript.javascriptDefaults.addExtraLib(
                    script_code,
                    lib_name
                  );
                });
            };
          };
          queue
            .push(addExtraLibrary('./monaco-rsvp.d.ts', 'rsvp'))
            .push(addExtraLibrary('./monaco-renderjs.d.ts', 'renderjs'))
            .push(addExtraLibrary('./monaco-jio.d.ts', 'jio'));
        }

        if (this.state.model_language === 'python') {
          const documentSymbolProvider = {
            provideDocumentSymbols: function (model, token) {
              const controller = new AbortController();
              token.onCancellationRequested(() => {
                controller.abort();
              });
              const data = new FormData();
              data.append('data', JSON.stringify({ code: model.getValue() }));
              return fetch(
                new URL(
                  'ERP5Site_getPythonCodeSymbolList',
                  location.href
                ).toString(),
                {
                  method: 'POST',
                  body: data,
                  signal: controller.signal
                }
              ).then(
                (response) => response.json(),
                (e) => {
                  if (!(e instanceof DOMException) /* AbortError */) {
                    throw e;
                  }
                  /* ignore aborted requests */
                }
              );
            }
          };
          monaco.languages.registerDocumentSymbolProvider(
            'python',
            documentSymbolProvider
          );

          const gadget = this;
          const yapfDocumentFormattingProvider = {
            _provideFormattingEdits: function (model, range, options, token) {
              const controller = new AbortController();
              token.onCancellationRequested(() => {
                controller.abort();
              });
              const data = new FormData();
              data.append(
                'data',
                JSON.stringify({ code: model.getValue(), range: range })
              );
              return fetch(
                new URL(
                  'ERP5Site_formatPythonSourceCode',
                  location.href
                ).toString(),
                {
                  method: 'POST',
                  body: data,
                  signal: controller.signal
                }
              )
                .then((response) => response.json())
                .then(
                  (data) => {
                    if (data.error) {
                      gadget.editor.revealLine(data.error_line);
                      return;
                    }
                    if (data.changed) {
                      return [
                        {
                          range: model.getFullModelRange(),
                          text: data.formatted_code
                        }
                      ];
                    }
                  },
                  (e) => {
                    if (!(e instanceof DOMException) /* AbortError */) {
                      throw e;
                    }
                    /* ignore aborted requests */
                  }
                );
            },
            provideDocumentRangeFormattingEdits: function (
              model,
              range,
              options,
              token
            ) {
              return this._provideFormattingEdits(model, range, options, token);
            },
            provideDocumentFormattingEdits: function (model, options, token) {
              return this._provideFormattingEdits(model, null, options, token);
            }
          };

          monaco.languages.registerDocumentFormattingEditProvider(
            'python',
            yapfDocumentFormattingProvider
          );
          monaco.languages.registerDocumentRangeFormattingEditProvider(
            'python',
            yapfDocumentFormattingProvider
          );

          queue.push(
            () => {
              // https://raw.githubusercontent.com/charliermarsh/ruff/main/ruff.schema.json
              const ruffConfig = {
                "preview": true,
                "builtins": [],
                "target-version": "py39",
                "line-length": 88,
                "indent-width": 2,
                "lint": {
                  "allowed-confusables": [],
                  "dummy-variable-rgx": "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?)|__traceback_info__|__traceback_supplement__)$",
                  "extend-select": [],
                  "extend-fixable": [],
                  "external": [],
                  "ignore": [
                    // indentation is not a multiple of 4
                    "E111", "E114",
                    // line too long
                    "E501",
                  ],
                  // https://docs.astral.sh/ruff/rules/
                  "select": [
                    "E",
                    "F",
                    "A",
                  ]
                },
                "format": {
                  "indent-style": "space",
                  "quote-style": "double"
                }
              };
              return window['registerRuffDiagnosticProvider'](
                this.editor,
                ruffConfig
              ).then(disposable => {
                // TODO: register disposable.dispose() to be called when gadget is destroyed (how to do this ?)
                ;
              });
            });
        }

        if (this.state.model_language === 'json') {
          let schemas = []
          if (this.state.schema_url) {
            schemas.push(
              {
                uri: this.state.schema_url,
                fileMatch: "*"
              }
            )
          }
          monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
            validate: true,
            allowComments: false,
            schemas: schemas,
            enableSchemaRequest: true,
          });
        }
      }
      queue.push(() => {
        if (modification_dict.hasOwnProperty('value')) {
          // Do not notify the UI when initializing the value
          this.state.ignoredChangeDuringInitialization = true;
          this.editor.setValue(this.state.value);
          this.state.ignoredChangeDuringInitialization = false;
        }
        this.editor.updateOptions({ readOnly: !this.state.editable });
      })
      return queue;
    })

    .declareMethod('getContent', function () {
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
})(window, rJS, window['monaco']);
