/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, FileReader, Blob*/

/**
 * Render options for editor gadget.
 *
 * @typedef {object} RenderOptions
 * @property {string} value the data to edit
 * @property {string} editor the selected editor
 * @property {string} content_type the mime type
 * @property {boolean} maximize start in maximized state
 * @property {string} portal_type the portal type
 * @property {boolean} editable set to true to have an editor when user
 *  can modify the content, false for a "read only" editor
 * @property {string} language the user language, if the editor supports
 *  localisation it will be displayed in this language
 * @property {string} password a password to decrypt the content
 * @property {boolean} run a hack for jsmd editor
 * @property {string} key Key for ERP5 form
 */

(function (window, rJS, RSVP, document, FileReader, Blob) {
  "use strict";

  var editor_dict = {
    "codemirror": {"url": "codemirror.gadget.html"},
    "monaco": {"url": "monaco-editor.gadget.html"},
    "onlyoffice": {"url": "onlyoffice.gadget.html"},
    "fck_editor": {"url": "ckeditor.gadget.html"},
    "html_viewer": {"url": "gadget_html_viewer.html"},
    "svg_editor" : {"url": "method-draw/method-draw.gadget.html"},
    "minipaint": {"url": "minipaint.gadget.html"},
    "jquery-sheets": {"url": "jquery-sheets.gadget.html"},
    "pdf": {"url": "pdf_js/pdfjs.gadget.html"},
    "notebook_editor": {"url": "gadget_notebook.html"},
    "jsmd_editor": {"url": "gadget_jsmd_viewer.html"},
    "jexcel" : {"url": "jexcel.gadget.html"}
  };


  function readBlobAsDataURL(blob) {
    var fr = new FileReader();
    return new RSVP.Promise(function (resolve, reject) {
      fr.addEventListener("load", resolve);
      fr.addEventListener("error", reject);
      fr.readAsDataURL(blob);
    }, function () {
      fr.abort();
    });
  }

  rJS(window)
    .declareAcquiredMethod('triggerMaximize', 'triggerMaximize')
    .allowPublicAcquisition('triggerMaximize', function (param_list) {
      var gadget = this;
      if (!this.element.classList.contains('editor-maximize')) {
        this.element.classList.toggle('editor-maximize');
      }
      return this.triggerMaximize.apply(this, param_list)
        .push(undefined, function () {
          if (gadget.element.classList.contains('editor-maximize')) {
            gadget.element.classList.remove('editor-maximize');
          }
        });
    })

    .declareMethod('render',
    /**
     * @param {RenderOptions} options
     */
    function(options) {
      return this.renderAsynchronously(options);
    })

    .declareJob('renderAsynchronously',
    /**
     * @param {RenderOptions} options
     */
    function (options) {
      var state_dict = {
          value: options.value || "",
          editor: options.editor,
          content_type: options.content_type,
          maximize: options.maximize,
          portal_type: options.portal_type,
          editable: options.editable || false,
          language: options.language,
          //run value is used to make jsmd viewer available in editable mode
          //this is temporary until the viewer becomes editable
          run: options.run || false,
          key: options.key,
          password: options.password,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };

      if ((!state_dict.editable) &&
          ((state_dict.editor === 'fck_editor') ||
           (state_dict.content_type === 'text/html'))) {
        state_dict.editor = 'html_viewer';
        state_dict.maximize = undefined;
      }

      if (!editor_dict.hasOwnProperty(state_dict.editor)) {
        // Do not show the maximize button when not embedding a subgadget
        state_dict.maximize = undefined;
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element,
        gadget = this,
        div = document.createElement('div'),
        div_max = document.createElement('div'),
        code,
        queue = new RSVP.Queue();

      if ((modification_dict.hasOwnProperty('editable')) ||
          (modification_dict.hasOwnProperty('editor')) ||
          (gadget.state.editor === 'notebook_editor')) {
        // Clear first to DOM, append after to reduce flickering/manip
        while (element.firstChild) {
          element.removeChild(element.firstChild);
        }
        if (modification_dict.hasOwnProperty('maximize') ||
            (gadget.state.editor === 'notebook_editor')) {
          // for fck_editor fields, we want to be able to maximize also in non editable
          if ((gadget.state.maximize && gadget.state.editable) ||
              (gadget.state.maximize && gadget.state.editor === 'jsmd_editor') ||
              (gadget.state.maximize &&
               (gadget.state.editor === 'fck_editor') &&
               gadget.state.editable)) {
            element.appendChild(div_max);
            queue
              .push(function () {
                return gadget.triggerMaximize(false);
              })
              .push(function () {
                return gadget.declareGadget("gadget_button_maximize.html", {
                  scope: 'maximize',
                  element: div_max,
                  sandbox: 'public'
                });
              }, function (error) {
              // Check Acquisition, old erp5 ui don't have triggerMaximize
                if (error.name !== "AcquisitionError") {
                  throw error;
                }
              });
          }
        }

        element.appendChild(div);

        if ((gadget.state.editable &&
             (editor_dict.hasOwnProperty(gadget.state.editor))) ||
            (!gadget.state.editable && gadget.state.editor === 'jsmd_editor') ||
            (!gadget.state.editable && gadget.state.editor === 'monaco') ||
            (gadget.state.editor === 'pdf')) {
          queue
            .push(function () {
              var gadget_url = editor_dict[gadget.state.editor].url;
              if (gadget.state.editor === 'jsmd_editor' &&
                  !gadget.state.run &&
                  gadget.state.editable) {
                gadget_url = editor_dict.codemirror.url;
              }
              return gadget.declareGadget(
                gadget_url,
                {
                  scope: 'editor',
                  sandbox: 'iframe',
                  element: div
                }
              );
            });
        } else if (!gadget.state.editable &&
                   ((gadget.state.editor === 'fck_editor') ||
                    (gadget.state.editor === 'html_viewer'))) {
          queue
            .push(function () {
              return gadget.declareGadget(editor_dict.html_viewer.url, {
                scope: 'editor',
                element: div
              });
            });
        } else if (gadget.state.editable &&
            (gadget.state.editor === 'text_area')) {
          element.appendChild(document.createElement('textarea'));
        } else if (!gadget.state.editable &&
            (gadget.state.editor === 'svg_editor')) {
          element.appendChild(document.createElement('img'));
        } else {
          element.appendChild(document.createElement('pre'));
        }
      }

      if ((gadget.state.editable &&
             (editor_dict.hasOwnProperty(gadget.state.editor))) ||
            (gadget.state.editor === 'fck_editor') ||
            (gadget.state.editor === 'html_viewer') ||
            (!gadget.state.editable && gadget.state.editor === 'jsmd_editor') ||
            (!gadget.state.editable && gadget.state.editor === 'monaco') ||
            (gadget.state.editor === 'pdf')) {
        queue
          .push(function () {
            return gadget.getDeclaredGadget('editor');
          })
          .push(function (editor_gadget) {
            return editor_gadget.render(gadget.state);
          });

        if (modification_dict.maximize === "auto") {
          queue
            .push(function () {
              return gadget.getDeclaredGadget("maximize");
            })
            .push(function (gadget_maximize) {
              return gadget_maximize.callMaximize(true);
            });
        }
      } else if (gadget.state.editable &&
          (gadget.state.editor === 'text_area')) {
        element.querySelector('textarea').value = gadget.state.value;
      } else if (!gadget.state.editable &&
          (gadget.state.editor === 'svg_editor')) {
        queue
          .push(function () {
            var blob = new Blob([gadget.state.value], {type: 'image/svg+xml'});
            return readBlobAsDataURL(blob);
          })
          .push(function (evt) {
            element.querySelector('img').src = evt.target.result;
          });
      } else {
        code = document.createElement('code');
        code.textContent = gadget.state.value;
        element.querySelector('pre').textContent = '';
        element.querySelector('pre').appendChild(code);
      }
      return queue;
    })

    .declareMethod('getContent', function () {
      var argument_list = arguments,
        gadget = this,
        result;
      if (this.state.editable &&
          editor_dict.hasOwnProperty(gadget.state.editor)) {
        return gadget.getDeclaredGadget('editor')
          .push(function (editor_gadget) {
            return editor_gadget.getContent.apply(editor_gadget, argument_list);
          });
          /*
          .push(function (result) {
            var value = result[context.state.key] || '';
            return readBlobAsDataURL(new Blob([value], {type: 'text/plain'}));
          })
          .push(function (evt) {
            var result = {};
            result[context.state.key] = evt.target.result;
            return result;
          });
          */
      }
      if (this.state.editable &&
          (this.state.editor === 'text_area')) {
        result = {};
        result[this.state.key] = this.element.querySelector('textarea').value;
        return result;
      }
      return {};
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      // XXX How to implement this for editors?
      return true;
    });

}(window, rJS, RSVP, document, FileReader, Blob));