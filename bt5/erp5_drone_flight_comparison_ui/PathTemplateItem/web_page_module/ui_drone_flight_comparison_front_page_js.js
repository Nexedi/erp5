(function (window, RSVP, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod('render', function render() {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Drone Simulator - Flight comparator',
            page_icon: 'puzzle-piece'
          });
        });
    });

}(window, RSVP, rJS));