/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, FileReader, Blob,
lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue*/
(function (window, rJS, RSVP, document, FileReader, Blob,
            lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue) {
  "use strict";

  var editor_dict = {
    "codemirror": {"url": "codemirror.gadget.html"},
    "monaco": {"url": "monaco-editor.gadget.html"},
    "onlyoffice": {"url": "onlyoffice.gadget.html"},
    "fck_editor": {"url": "ckeditor.gadget.html"},
    "svg_editor" : {"url": "method-draw/method-draw.gadget.html"},
    "minipaint": {"url": "minipaint.gadget.html"},
    "jquery-sheets": {"url": "jquery-sheets.gadget.html"},
    "pdf": {"url": "pdf_js/pdfjs.gadget.html"},
    "notebook_editor": {"url": "gadget_notebook.html"},
    "jsmd_editor": {"url": "gadget_jsmd_viewer.html"}
  };


  function readBlobAsDataURL(blob) {
    var fr = new FileReader();
    return new RSVP.Promise(function (resolve, reject, notify) {
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
        .push(function () {
          if (gadget.element.classList.contains('editor-maximize')) {
            gadget.element.classList.remove('editor-maximize');
          }
        });
    })
    .declareMethod('render', function (options) {

      var state_dict = {
          value: options.value || "",
          editor: options.editor,
          content_type: options.content_type,
          maximize: options.maximize,
          portal_type: options.portal_type,
          editable: options.editable || false,
          key: options.key,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      return this.renderAsynchronously(modification_dict);
    })

    .declareJob('renderAsynchronously', function (modification_dict) {
      var element = this.element,
        gadget = this,
        url,
        div = document.createElement('div'),
        div_max = document.createElement('div'),
        queue = lockGadgetInQueue(gadget)();

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
              (gadget.state.maximize && gadget.state.editor === 'fck_editor')) {
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
            (!gadget.state.editable && gadget.state.editor === 'fck_editor') ||
            (!gadget.state.editable && gadget.state.editor === 'jsmd_editor') ||
            (!gadget.state.editable && gadget.state.editor === 'monaco') ||
            (gadget.state.editor === 'pdf')) {
          queue
            .push(function () {
              var url = editor_dict[gadget.state.editor].url;
              if (gadget.state.editable && (gadget.state.editor === 'jsmd_editor')) {
                url = editor_dict.codemirror.url;
              }
              return gadget.declareGadget(
                url,
                {
                  scope: 'editor',
                  sandbox: 'iframe',
                  element: div
                }
              );
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
            (!gadget.state.editable && gadget.state.editor === 'fck_editor') ||
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
        element.querySelector('pre').textContent = gadget.state.value;
      }
      return queue
        .push(unlockGadgetInQueue(gadget), unlockGadgetInFailedQueue(gadget));
    })

    .declareMethod('getContent', function () {
      var argument_list = arguments,
        gadget = this,
        result;
      if (this.state.editable &&
          editor_dict.hasOwnProperty(gadget.state.editor)) {
        return lockGadgetInQueue(gadget)()
          .push(function () {
            return gadget.getDeclaredGadget('editor');
          })
          .push(function (editor_gadget) {
            return editor_gadget.getContent.apply(editor_gadget, argument_list);
          })
          .push(unlockGadgetInQueue(gadget), unlockGadgetInFailedQueue(gadget));
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
      } else if (this.state.editable &&
          (this.state.editor === 'text_area')) {
        result = {};
        result[this.state.key] = this.element.querySelector('textarea').value;
        return result;
      }
      return {};
    })

    .declareMethod('checkValidity', function () {
      // XXX How to implement this for editors?
      return true;
    });

}(window, rJS, RSVP, document, FileReader, Blob,
  lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue));