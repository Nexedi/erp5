/*jslint indent: 2, maxerr: 3, nomen: true, maxlen: 80 */
/*global window, rJS, RSVP */
(function (window, rJS, RSVP) {
  "use strict";
  rJS(window)

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .allowPublicAcquisition('trigger', function trigger() {
      return this.toggle();
    })

    .declareMethod('toggle', function toggle() {
      if (this.state.visible) {
        return this.close();
      }
      return this.changeState({
        visible: !this.state.visible
      });
    })

    .declareMethod('close', function close() {
      return this.changeState({
        visible: false,
        url: undefined,
        options: undefined
      });
    })

    .declareMethod('render', function render(url, options) {
      // XXX Hack to close the panel if the sort/filter button
      // is clicked twice
      if (url === this.state.url) {
        return this.changeState({
          visible: false,
          url: undefined,
          options: undefined
        });
      }
      return this.changeState({
        visible: true,
        url: url,
        options: options
      });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var queue,
        gadget = this;
      if (this.state.visible) {
        if (!this.element.classList.contains('visible')) {
          this.element.classList.toggle('visible');
        }
      } else {
        if (this.element.classList.contains('visible')) {
          this.element.classList.remove('visible');
        }
      }

      if (modification_dict.hasOwnProperty('url')) {
        if (this.state.url === undefined) {
          while (this.element.firstChild) {
            this.element.removeChild(this.element.firstChild);
          }
        } else {
          queue = this.declareGadget(this.state.url,
                                     {scope: "declared_gadget"});
        }
      } else {
        if (this.state.url !== undefined) {
          queue = this.getDeclaredGadget("declared_gadget");
        }
      }

      if (queue !== undefined) {
        return queue
          .push(function (declared_gadget) {
            return RSVP.all([
              declared_gadget,
              declared_gadget.render(gadget.state.options)
            ]);
          })
          .push(function (result_list) {
            if (modification_dict.hasOwnProperty('url')) {
              while (gadget.element.firstChild) {
                gadget.element.removeChild(gadget.element.firstChild);
              }
              gadget.element.appendChild(result_list[0].element);
            }
          });
      }
    });

}(window, rJS, RSVP));