/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, FileReader, Blob,
lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue*/
(function (window, rJS, RSVP, document, FileReader, Blob,
            lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue) {
  "use strict";

/*
  function readBlobAsDataURL(blob) {
    var fr = new FileReader();
    return new RSVP.Promise(function (resolve, reject, notify) {
      fr.addEventListener("load", resolve);
      fr.addEventListener("error", reject);
      fr.addEventListener("progress", notify);
      fr.readAsDataURL(blob);
    }, function () {
      fr.abort();
    });
  }
*/

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
          key: options.key
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
          (modification_dict.hasOwnProperty('editor'))) {
        // Clear first to DOM, append after to reduce flickering/manip
        while (element.firstChild) {
          element.removeChild(element.firstChild);
        }
        if (modification_dict.hasOwnProperty('maximize')) {
          if (gadget.state.maximize && gadget.state.editable) {
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

        if (gadget.state.editable &&
            (gadget.state.editor === 'codemirror')) {
          queue
            .push(function () {
              return gadget.declareGadget(
                "codemirror.gadget.html",
                {
                  scope: 'editor',
                  sandbox: 'iframe',
                  element: div
                }
              );
            });
        } else if (gadget.state.editable &&
            (gadget.state.editor === 'fck_editor')) {
          queue
            .push(function () {
              return gadget.declareGadget(
                "ckeditor.gadget.html",
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
        } else {
          element.appendChild(document.createElement('pre'));
        }
      }

      if (gadget.state.editable &&
          ((gadget.state.editor === 'codemirror') || (gadget.state.editor === 'fck_editor'))) {
        queue
          .push(function () {
            return gadget.getDeclaredGadget('editor');
          })
          .push(function (editor_gadget) {
            return editor_gadget.render(gadget.state);
          });
      } else if (gadget.state.editable &&
          (gadget.state.editor === 'text_area')) {
        element.querySelector('textarea').value = gadget.state.value;
      } else if (!gadget.state.editable &&
          (gadget.state.editor === 'fck_editor')) {
        element.innerHTML = gadget.state.value;
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
          ((this.state.editor === 'codemirror') || (this.state.editor === 'fck_editor'))) {
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
    });

}(window, rJS, RSVP, document, FileReader, Blob,
  lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue));
