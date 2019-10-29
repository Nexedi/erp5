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
          automaticLayout: true,
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
        run: context.deferNotifySubmit.bind(context),
      });

      editor.getModel().updateOptions({
        tabSize: 2,
        insertSpaces: true,
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
                  source: 'jslint',
                }))
            );
          }
        });
    })
    .declareJob('runPyLint', function () {
      var context = this;
      return (function (controller) {
        return new RSVP.Queue()
          .push(function () {
            return RSVP.delay(2000);
          })
          .push(function () {
            if (
              context.state.model_language === 'python' &&
              context.state.language_support_url
            ) {
              const data = new FormData();
              const checker_parameters = {
                code: context.editor.getValue(),
                portal_type: context.state.portal_type,
              };

              data.append('data', JSON.stringify(checker_parameters));
              fetch(
                context.state.language_support_url +
                  '/ERP5Site_checkPythonSourceCodeAsJSON',
                {
                  method: 'POST',
                  body: data,
                  signal: controller.signal,
                }
              )
                .then((response) => response.json())
                .then(
                  (data) => {
                    monaco.editor.setModelMarkers(
                      context.editor.getModel(),
                      'pylint',
                      data['annotations'].map((annotation) => {
                        return {
                          startLineNumber: annotation.row + 1,
                          endLineNumber: annotation.row + 1,
                          startColumn: annotation.col,
                          endColumn: Infinity,
                          message: annotation.text,
                          severity:
                            annotation.type === 'error'
                              ? monaco.MarkerSeverity.Error
                              : monaco.MarkerSeverity.Warning,
                        };
                      })
                    );
                  },
                  (e) => {
                    if (!(e instanceof DOMException) /* AbortError */) {
                      throw e;
                    }
                    /* ignore aborted requests */
                  }
                );
            }
          })
          .push(undefined, function (e) {
            if (e instanceof RSVP.CancellationError) {
              controller.abort();
            }
            throw e;
          });
      })(new AbortController());
    })
    .declareMethod('render', function (options) {
      var model_language,
        state_dict = {
          key: options.key,
          editable: options.editable === undefined ? true : options.editable,
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
      }
      state_dict.model_language = model_language;
      state_dict.portal_type = options.portal_type;
      state_dict.value = options.value || '';
      state_dict.language_support_url = options.language_support_url || '';
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var queue = new RSVP.Queue(),
        gadget = this;
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
                    text,
                  },
                ];
              },
            }
          );

          // lint with jslint
          this.editor.getModel().onDidChangeContent(this.runJsLint.bind(this));
          this.runJsLint();

          // lint with typescript compiler
          monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
            noSemanticValidation: false,
            noSyntaxValidation: false,
          });

          monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
            target: monaco.languages.typescript.ScriptTarget.ES6,
            allowNonTsExtensions: true,
            checkJs: true,
            allowJs: true,
            module: monaco.languages.typescript.ModuleKind.UMD,
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
        if (modification_dict.hasOwnProperty('editable')) {
          this.editor.updateOptions({ readOnly: !this.state.editable });
        }
        if (this.state.model_language === 'python') {
          this.editor.getModel().onDidChangeContent(this.runPyLint.bind(this));

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
                gadget.state.language_support_url +
                  '/ERP5Site_formatPythonSourceCode',
                {
                  method: 'POST',
                  body: data,
                  signal: controller.signal,
                }
              )
                .then((response) => response.json())
                .then(
                  (data) => {
                    if (data.error) {
                      this.editor.revealLine(data.error_line);
                      return;
                    }
                    if (data.changed) {
                      return [
                        {
                          range: model.getFullModelRange(),
                          text: data.formatted_code,
                        },
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
            },
          };

          monaco.languages.registerDocumentFormattingEditProvider(
            'python',
            yapfDocumentFormattingProvider
          );
          monaco.languages.registerDocumentRangeFormattingEditProvider(
            'python',
            yapfDocumentFormattingProvider
          );

          monaco.languages.registerCompletionItemProvider('python', {
            provideCompletionItems: async function (
              model,
              position,
              context,
              token
            ) {
              const controller = new AbortController();
              token.onCancellationRequested(() => {
                controller.abort();
              });
              const data = new FormData();
              const complete_parameters = {
                code: model.getValue(),
                position: {
                  line: position.lineNumber,
                  column: position.column,
                },
              };

              data.append('data', JSON.stringify(complete_parameters));
              return fetch(
                gadget.state.language_support_url +
                  '/ERP5Site_getPythonSourceCodeCompletionList',
                {
                  method: 'POST',
                  body: data,
                  signal: controller.signal,
                }
              )
                .then((response) => response.json())
                .then(
                  (data) => {
                    return {
                      suggestions: data.map((c) => {
                        c.kind = monaco.languages.CompletionItemKind[c._kind];
                        // this makes monaco render documentation as markdown.
                        c.documentation = { value: c.documentation };
                        return c;
                      }),
                    };
                  },
                  (e) => {
                    if (!(e instanceof DOMException) /* AbortError */) {
                      throw e;
                    }
                    /* ignore aborted requests */
                  }
                );
            },
          });

          monaco.languages.registerDefinitionProvider('python', {
            provideDefinition: async function (model, position, token) {
              const controller = new AbortController();
              token.onCancellationRequested(() => {
                controller.abort();
              });
              const data = new FormData();
              const complete_parameters = {
                code: model.getValue(),
                position: {
                  line: position.lineNumber,
                  column: position.column,
                },
              };
              complete_parameters['xxx_definition'] = true;
              data.append('data', JSON.stringify(complete_parameters));
              // TODO: this should use a proper endpoint ...
              return fetch(
                gadget.state.language_support_url +
                  '/ERP5Site_getPythonSourceCodeCompletionList',
                {
                  method: 'POST',
                  body: data,
                  signal: controller.signal,
                }
              )
                .then((response) => response.json())
                .then(
                  (data) => {
                    var definitions = [];
                    for (let i = 0; i < data.length; i++) {
                      if (data[i].code) {
                        // TODO: these models are not refreshed, if the file they refefer is modified,
                        // they show outdated content.
                        let definition_uri = monaco.Uri.from({
                          scheme: 'file',
                          path: data[i].uri,
                        });
                        let definition_model = monaco.editor.getModel(
                          definition_uri
                        );

                        if (!definition_model) {
                          definition_model = monaco.editor.createModel(
                            data[i].code,
                            'python',
                            definition_uri
                          );
                        }
                        data[i].uri = definition_model.uri;
                      }
                      definitions.push({
                        range: data[i].range,
                        uri: data[i].uri ? data[i].uri : model.uri,
                      });
                    }
                    return definitions;
                  },
                  (e) => {
                    if (!(e instanceof DOMException) /* AbortError */) {
                      throw e;
                    }
                    /* ignore aborted requests */
                  }
                );
            },
          });

          this.runPyLint();
        }
      }
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
