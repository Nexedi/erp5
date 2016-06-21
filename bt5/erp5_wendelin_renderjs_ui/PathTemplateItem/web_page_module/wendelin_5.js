/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener,
          loopEventListener, jQuery, promiseReadAsText*/
/*jslint indent: 2, maxerr: 3 */

(function () {
  "use strict";

  function randomString(length) {
    var i,
      str = '',
      chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.split('');

    if (!length) {
      length = Math.floor(Math.random() * chars.length);
    }

    for (i = 0; i < length; i = i + 1) {
      str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
  }

  function waitForImport(gadget) {
    var name,
      upload_file;

    return new RSVP.Queue()
      .push(function () {
        return gadget.getElement();
      })
      .push(function (element) {
        return promiseEventListener(
          element.getElementsByClassName("import_form")[0],
          'submit',
          false
        );
      })
      .push(function (evt) {
        // Prevent double click
        var now = new Date();
        evt.target
           .getElementsByClassName("ui-btn")[0].disabled = true;

        upload_file = evt.target.dream_import.files[0];
        name = upload_file.name;

        // Create jIO document
        //XX: fail here!!!!
        return gadget.aq_put({
          _id: randomString(12),
          title: name,
          type: "Dream",
          format: "application/json",
          modified: now.toUTCString(),
          date: now.getFullYear() + "-" + (now.getMonth() + 1) + "-" +  now.getDate()
        });
      })
      .push(function (id) {
        gadget.foo_id = id;
        // Add JSON as attachment
        return gadget.aq_putAttachment({
          "_id": id,
          "_attachment": "body.json",
          "_data": upload_file,
          "_mimetype": "application/json"
        });
      });
  }
    // Ivan: we extend gadget API like so:
  rJS(window).declareMethod('render', function () {
    return 'this is render method in a subgadget';
  })

    // ivan: decalre we want to use JIO functionality as an alias (aq_post)
    .declareAcquiredMethod("aq_post", "jio_post")
    .declareAcquiredMethod("aq_put", "jio_put")
    .declareAcquiredMethod("aq_putAttachment", "aq_putAttachment")
    .declareAcquiredMethod("whoWantsToDisplayThisDocument", "whoWantsToDisplayThisDocument")
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")
    .declareAcquiredMethod("goAndSaveToHistory", "goAndSaveToHistory")

    // catch form submission
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          // wait for user input of upload file.
          return waitForImport(gadget);
        })
        .push(function () {
          // ask RenderJs create an URL for us which represents the current "state" of the application
          return gadget.whoWantsToDisplayThisDocument(gadget.foo_id, 'show');
        })
        .push(function (url) {
          // redirect to url produced from previous call
          return gadget.goAndSaveToHistory(url);
        });
    });
}());