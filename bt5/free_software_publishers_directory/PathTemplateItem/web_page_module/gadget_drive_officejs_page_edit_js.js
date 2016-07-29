/*globals window, rJS, RSVP, loopEventListener, Blob*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, loopEventListener, Blob) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      g.options = null;
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          // g.props.deferred = RSVP.defer();
        });
    })

    // allow external use of triggerData, so that editor gadget can save
    // with its own shortcuts/buttons/whatever.
    .allowPublicAcquisition('triggerSubmit', function () {
      this.triggerSubmit();
    })

    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })

    .declareMethod('render', function (options) {
      var gadget = this,
        format = 'text';
      gadget.props.resourceName = options.resource;

      return gadget.jio_getAttachment(
        [gadget.props.resourceName].join('/'),
        'enclosure',
        {format: format}
      )
        .push(function (data) {
          return gadget.getDeclaredGadget('codemirror')
            .push(function (editorGadget) {
              gadget.props.editorGadget = editorGadget;
              return editorGadget.render({
                data: data,
                resource: gadget.props.resourceName
              });
            });
        })


        .push(function () {
          return gadget.updateHeader({
            title: 'Editing ' + gadget.props.resourceName,
            save_action: true,
            panel_action: false,
            back_url: (typeof options.back === 'string' ?
                       "#position=" + options.back : '#')
          });
        });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('form'),
            'submit',
            true,
            function () {
              return gadget.props.editorGadget.getData()
                .push(function (data) {
                  var blob = new Blob([data], {"type" : "text/plain"});
                  return gadget.jio_putAttachment(
                    gadget.props.resourceName,
                    'enclosure',
                    blob
                  );
                });
            }
          );
        });
    });

}(window, RSVP, rJS, loopEventListener, Blob));