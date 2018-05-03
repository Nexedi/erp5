/*global document, window, rJS, RSVP, loopEventListener, navigator, MediaRecorder, Blob, setInterval, Promise */
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS, RSVP) {
  "use strict";

  function promiseMyStream(stream_options, callback) {
    var stream,
      callback_queue;

    function canceller() {
      if ((callback_queue !== undefined) &&
          (typeof callback_queue.cancel === "function")) {
        callback_queue.cancel();
      }

      if (stream !== undefined) {
        stream.getTracks().forEach(function (track) { track.stop(); });
      }
    }

    return new RSVP.Promise(function (resolve, reject) {
      /*jslint unparam: true*/
      navigator.mediaDevices.getUserMedia(stream_options)
        .then(function (result) {
          stream = result;
          callback_queue = new RSVP.Queue()
            .push(function () {
              return callback(stream);
            });
          return callback_queue;
        })
        .then(undefined, function (error) {
          canceller();
          reject(error);
        });

    }, canceller);
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .onLoop(function () {
      var gadget = this,
        div = gadget.element.querySelector("div[class='ui-record-circle']")
            .firstElementChild,
        now = new Date().getTime(),
        distance = now - gadget.state.start,
        minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))
            .toString(),
        seconds = Math.floor((distance % (1000 * 60)) / 1000).toString();

      minutes = ("00" + minutes).slice(-2);
      seconds = ("00" + seconds).slice(-2);

      div.textContent = minutes + ":" + seconds;
    }, 1000)

    .onEvent('submit', function () {
      var gadget = this;
      gadget.state.record.stop();
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.notifySubmitting();
        })
        .push(function () {
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          var portal_type = result[0].split(',')[2],
            parent_relative_url = result[1].split(',')[2],
            date,
            title;
          if (gadget.state.audio) {
            date = new Date();
            title = date.getFullYear() + "_" + date.getMonth() + "_" +
              date.getDate() + "_" + date.getHours() + ":" +
              date.getMinutes() + ":" + date.getSeconds();
            return gadget.jio_post({
              "title": "record_" + title,
              portal_type: portal_type,
              parent_relative_url: parent_relative_url
            });
          }
        })
        .push(function (id_audio) {
          if (id_audio) {
            return gadget.jio_putAttachment(id_audio, 'data',
                                            gadget.state.audio);
          }
        })
        .push(function () {
          return RSVP.all([
            gadget.redirect({command: 'display',
                             options: {page: 'ojs_smart_assistant_home'}}),
            gadget.notifySubmitted({"message": "Data created",
                                    "status": "success"})
          ]);
        });
    })
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareJob('record', function () {
      var gadget  = this,
        stream,
        record;
      return RSVP.Queue()
        .push(function () {
          return gadget.notifyChange();
        })
        .push(function () {
          return promiseMyStream({audio: true}, function (result) {
            stream = result;
            record = new MediaRecorder(stream);
            record.start();
            gadget.state.record = record;

            return RSVP.any([
              loopEventListener(record,
                'stop',
                false,
                function () {
                  return gadget.props.deferred.resolve();
                }),
              loopEventListener(record,
                'dataavailable',
                false,
                function (event) {
                  gadget.state.audio = event.data;
                })
            ]);

          });
        })
        .push(undefined, function (error) {
          if (!(error instanceof RSVP.CancellationError)) {
            return RSVP.all([
              gadget.redirect({command: 'display',
                               options: {page: 'ojs_smart_assistant_home'}}),
              gadget.notifySubmitted({
                "message": "We can't access to your microphone",
                "status": "fail"
              })
            ]);
          }
          throw error;
        });
    })
    .declareMethod("render", function () {
      var gadget = this;
      gadget.state.start = new Date().getTime();
      gadget.props = {
        deferred: RSVP.defer()
      };
      return gadget.getUrlFor(({command: 'display',
                                options: {page: 'ojs_smart_assistant_home'}}))

        .push(function (url) {
          return gadget.updateHeader({
            page_title: 'Recording audio',
            save_action: true,
            selection_url: url
          });
        })
        .push(function () {
          return gadget.record();
        });
    });
}(window, rJS, RSVP));