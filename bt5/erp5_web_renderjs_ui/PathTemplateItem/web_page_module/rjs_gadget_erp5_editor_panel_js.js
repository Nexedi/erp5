/*jslint indent: 2, maxerr: 3, nomen: true, maxlen: 80 */
/*global window, rJS, RSVP */
(function (window, rJS, RSVP) {
  "use strict";
  rJS(window)

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .allowPublicAcquisition('trigger', function trigger() {
      return this.close();
    })

    .declareMethod('toggle', function toggle() {
      return this.changeState({
        url: undefined
      });
    })

    .declareMethod('close', function close() {
      return this.changeState({
        url: undefined
      });
    })

    .declareMethod('render', function render(url, options) {
      return this.changeState({
        // Hack to close the panel if the sort/filter button
        // is clicked twice
        url: (url === this.state.url) ? undefined : url,
        options: options
      });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var queue,
        gadget = this;

      if (modification_dict.hasOwnProperty('url')) {
        if (this.state.url === undefined) {
          if (this.element.classList.contains('visible')) {
            this.element.classList.remove('visible');
          }
          while (this.element.firstChild) {
            this.element.removeChild(this.element.firstChild);
          }
        } else {
          if (!this.element.classList.contains('visible')) {
            this.element.classList.toggle('visible');
          }
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