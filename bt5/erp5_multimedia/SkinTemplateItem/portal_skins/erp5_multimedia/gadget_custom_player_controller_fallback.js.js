/*global window, rJS, RSVP, URL, Blob, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, URL, loopEventListener) {
  "use strict";

  rJS(window)
    .setState({ currentTime: 0 })
    //////////////////////////////////////////////
    // Acquire methods
    /////////////////////////////////////////////
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('jio_getAttachment', 'jio_getAttachment')
    .declareAcquiredMethod('togglePlayPause', 'togglePlayPause')
    .declareAcquiredMethod('toggleSound', 'toggleSound')
    .declareAcquiredMethod('updateCurrentTime', 'updateCurrentTime')
    .declareAcquiredMethod('updateTotalTime', 'updateTotalTime')
    .declareAcquiredMethod('notifySubmitted', 'notifySubmitted')
    .declareAcquiredMethod('onEnd', 'onEnd')

    //////////////////////////////////////////////
    // Declare methods
    /////////////////////////////////////////////
    .declareMethod('getAudioChunk', function () {
      var gadget = this;
      // Call `getAttachment` method of jIO to fetch a chunk of data from IDB storage.
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_getAttachment(gadget.params.id, gadget.params.name, {
            start: 0
          });
        })
        .push(undefined, function (error) {
          if ((error.constructor.name === 'jIOError' && error.status_code === 404) ||
              (error.target && error.target.error.name === "NotReadableError")) {
            return gadget.notifySubmitted({message: error.message || error.target.error.message, status: 'fail'});
          }
          throw error;
        });
    })
    
    .declareMethod('updateAudioElementCurrentTime', function (time) {
      this.element.querySelector('audio').currentTime = time;
    })

    .declareMethod('handlePlayPause', function (play) {
      var audio = this.element.querySelector('audio');
      if (play) {
        audio.play();
      } else {
        audio.pause();
      }
    })

    .declareMethod('handleSound', function (mute) {
      this.element.querySelector('audio').muted = mute;
    })

    .declareMethod('render', function (params) {
      var gadget = this,
        queue = new RSVP.Queue();
      gadget.params = params;

      if (gadget.params.id) {
        if (!gadget.params.name) {
          queue
            .push(function () {
              return gadget.getSetting('hateoas_url');
            });
        }
        queue
          .push(function (hateoas_url) {
            if (!gadget.params.name) {
              gadget.params.name = hateoas_url + gadget.params.id;
            }
            return gadget.getAudioChunk()
              .push(function (blob) {
                if (!(blob instanceof Blob)) {
                  blob = new Blob();
                }
                gadget.element.querySelector('audio').src = URL.createObjectURL(blob);
                gadget.element.querySelector('audio').onloadeddata = function () {
                  gadget.updateTotalTime(gadget.element.querySelector('audio').duration);
                }.bind(gadget);
              });
          });
      }
      return queue;
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('currentTime')) {
        return this.updateCurrentTime(modification_dict.currentTime);
      }
    })

    .declareService(function () {
      var gadget = this,
        audio = gadget.element.querySelector('audio');
      return loopEventListener(
        audio,
        'timeupdate',
        false,
        function () {
          return gadget.changeState({ currentTime: audio.currentTime });
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this,
        audio = gadget.element.querySelector('audio');
      return RSVP.Queue()
        .push(function () {
          return loopEventListener(
            audio,
            'ended',
            false,
            function () {
              audio.currentTime = 0;
              return gadget.onEnd();
            },
            true
          );
        })
        .push(undefined, function (error) {
          if (error instanceof RSVP.CancellationError) {
            // Pause when gadget go out of scope { CancellationError }.
            audio.pause(); 
          } else {
            throw error;
          }
        });
    });
}(window, rJS, RSVP, URL, rJS.loopEventListener));