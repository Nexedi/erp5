/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document*/
(function (window, rJS, RSVP, document) {
  "use strict";

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

    .declareMethod('render', function (options) {
      return this.renderAsynchronously(options);
    })

    .declareJob('renderAsynchronously', function (options) {
      var state_dict = {
          value: options.value || "",
          maximize: options.maximize,
          key: options.key,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element,
        gadget = this,
        div = document.createElement('div'),
        div_max = document.createElement('div'),
        code,
        queue = new RSVP.Queue();

      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }
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
      element.appendChild(div);

      queue
        .push(function () {
          return gadget.declareGadget(
            "drone_simulator_engine.html",
            {
              scope: 'simulator',
              sandbox: 'iframe',
              element: div
            }
          );
        });
      queue
        .push(function () {
          return gadget.getDeclaredGadget('simulator');
        })
        .push(function (simulator_gadget) {
          return simulator_gadget.render(gadget.state);
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
      return queue;
    })

    .declareMethod('getContent', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('simulator')
      .push(function (simulator_gadget) {
        return simulator_gadget.getContent();
      });
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      // XXX How to implement this for editors?
      return true;
    });

}(window, rJS, RSVP, document));
