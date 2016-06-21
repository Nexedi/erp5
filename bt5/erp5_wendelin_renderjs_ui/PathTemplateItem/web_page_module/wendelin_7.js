/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener,
          loopEventListener, jQuery, console, jIO*/
/*jslint indent: 2, maxerr: 3 */
(function () {
  "use strict";

  // Ivan: we extend gadget API like so:
  rJS(window).declareMethod('render', function (options) {
    var gadget = this;

    return gadget.aq_getAttachment({
      "_id": options.id,
      "_attachment": "body.json"
    })
      .push(function (result) {
        // XXX: not nice use directly jio!
        //return jIO.util.readBlobAsText(result.data); -> old way
        return jIO.util.readBlobAsArrayBuffer(result.data);
      })
      .push(function (event) {
        gadget.data = event.target.result;
        // getDeclaredGadget uses scope to get a sub gadget, which is a promise
        return gadget.getDeclaredGadget('Visualise');
      })
      .push(function (sub_gadget) {
        sub_gadget.draw(gadget.data);
      });
  })

    // ivan: decalre we want to use JIO functionality as an alias (aq_post)
    .declareAcquiredMethod("aq_get", "jio_get")
    .declareAcquiredMethod("aq_getAttachment", "aq_getAttachment");

}());