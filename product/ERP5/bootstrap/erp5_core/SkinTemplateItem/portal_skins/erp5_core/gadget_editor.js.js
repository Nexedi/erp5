/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, FileReader, Blob*/
(function (window, rJS, RSVP, document, FileReader, Blob) {
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
    .declareMethod('render', function (options) {
      
      var state_dict = {
          value: options.value || "",
          editor: options.editor,
          content_type: options.content_type,
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
        queue = new RSVP.Queue();

      if ((modification_dict.hasOwnProperty('editable')) ||
          (modification_dict.hasOwnProperty('editor'))) {
        // Clear first to DOM, append after to reduce flickering/manip
        while (element.firstChild) {
          element.removeChild(element.firstChild);
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
      } else if (!gadget.state.editable &&
          (gadget.state.editor === 'fck_editor')) {
        element.innerHTML = gadget.state.value;
      } else {
        element.querySelector('pre').textContent = gadget.state.value;
      }
      return queue;
    })

    .declareMethod('getContent', function () {
      var argument_list = arguments,
        context = this;
      if (this.state.editable &&
          ((this.state.editor === 'codemirror') || (this.state.editor === 'fck_editor'))) {
        return this.getDeclaredGadget('editor')
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
      return {};
    });

}(window, rJS, RSVP, document, FileReader, Blob));
