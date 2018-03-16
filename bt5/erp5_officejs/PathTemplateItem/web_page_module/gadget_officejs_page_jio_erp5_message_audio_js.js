/*global window, rJS, RSVP, loopEventListener, navigator, MediaRecorder, Blob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP, jIO) {
  "use strict";

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
    
  
    .declareService(function () {
      this.notifyChange();
      var div = document.querySelector("div[id=audio_view]");
    
      var start = new Date().getTime();
    
      var x = setInterval(function () {
        var now = new Date().getTime();
        var distance = now - start;
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)).toString();
        var seconds = Math.floor((distance % (1000 * 60)) / 1000).toString();
        
        minutes = ("00" + minutes).slice(-2);
        seconds = ("00" + seconds).slice(-2);
        
        div.innerHTML = minutes + ":" + seconds;
        
      }, 1000);
    })

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
          var portal_type = result[0].split(',')[2];
          var parent_relative_url = result[1].split(',')[2];
          if (gadget.state.audio) {
            var date = new Date();
            var title = date.getFullYear() + "_" + date.getMonth() + "_" + date.getDate() + "_" + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
            return gadget.jio_post({
              "title": "record_" + title,
              portal_type: portal_type,
              parent_relative_url: parent_relative_url
            });
          }
        })
        .push(function (id_audio) {
          if (id_audio) {
            return gadget.jio_putAttachment(id_audio, 'data', gadget.state.audio);
          }
        })
       .push(function (result) {
          return gadget.redirect({command: 'display', options: {page: 'ojs_message_front', jio_key: result}});
        });
    })
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })
  .declareJob('record', function () {
    var gadget  = this,
      record;
    record = new MediaRecorder(gadget.state.stream);
    record.start();
    gadget.state.record = record;
    return new RSVP.Queue()
      .push(function () {
        return RSVP.any([
          loopEventListener(record,
              'stop',
              false,
              function () {
                gadget.state.stream.getTracks().forEach(function (track) { track.stop();});
                return gadget.props.deferred.resolve();
              }),
            loopEventListener(record,
              'dataavailable',
              false,
              function (event) {
                gadget.state.audio = event.data;
            })
          ]);
        })
        .push(undefined, function (e) {
           if (e instanceof RSVP.CancellationError) {
             gadget.state.stream.getTracks().forEach(function (track) { track.stop();});
           }
        });
  })
  .declareMethod("render", function (options) {
      var gadget = this;
       gadget.props = {
         deferred: RSVP.defer()
       };
      return gadget.getUrlFor(({command: 'display', options: {page: 'ojs_message_front'}}))

        .push(function (url) {
          return gadget.updateHeader({
            page_title: 'Recording audio',
            save_action: true,
            selection_url: url
          });
        })
        .push(function () {
          return new Promise(function (resolve, reject, notify) {
            navigator.mediaDevices.getUserMedia({ audio: true })
              .then(resolve)
              .catch(function(err) {
                gadget.notifySubmitted({
                  "message": "We can't access to your microphone",
                  "status": "fail"
                });
              });
             });
         })
        .push(function (stream) {
          gadget.state.stream = stream;
          return gadget.record();
        });
    });
}(document, window, rJS, RSVP, jIO));
