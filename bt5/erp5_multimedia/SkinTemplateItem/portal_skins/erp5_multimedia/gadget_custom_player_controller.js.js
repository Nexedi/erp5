/*global window, rJS, RSVP, jIO, AudioContext,
  URL, MediaSource, document,
  promiseEventListener, ArrayBuffer */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, AudioContext, URL, MediaSource, loopEventListener) {
  "use strict";

  rJS(window)
    .setState({ currentTime: 0 })
    //////////////////////////////////////////////
    // Acquire methods
    /////////////////////////////////////////////
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('jio_getAttachment', 'jio_getAttachment')
    .declareAcquiredMethod('updateCurrentTime', 'updateCurrentTime')
    .declareAcquiredMethod('updateTotalTime', 'updateTotalTime')
    .declareAcquiredMethod('notifySubmitted', 'notifySubmitted')
    .declareAcquiredMethod('onEnd', 'onEnd')

    //////////////////////////////////////////////
    // Declare methods
    /////////////////////////////////////////////
    .declareMethod('configurePlayerContext', function () {
      this.params.source.connect(this.params.gain);
      this.params.gain.connect(this.params.audioContext.destination);
    })

    .declareMethod('getAudioChunk', function () {
      var gadget = this, start, end;
      start = gadget.params.index;
      if (gadget.params.end || gadget.params.mediaSource.sourceBuffers.length === 0) {
        return;
      }

      end = start + 10e5;
      // Call `getAttachment` method of jIO to fetch a chunk of data from IDB storage.
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_getAttachment(gadget.params.id, gadget.params.name, {
            'start': start,
            'end': end,
            'format': 'array_buffer'
          }).push(function (buffer) {
            if (buffer.byteLength < 10e5) {
              gadget.params.end = true;
            }
            gadget.params.index += 10e5;
            return buffer;
          }, function (error) {
            if ((error.constructor.name === 'jIOError' && error.status_code === 404) ||
                (error.target && error.target.error.name === "NotReadableError")) {
              return gadget.notifySubmitted({message: error.message || error.target.error.message, status: 'fail'});
            }
            throw error;
          });
        });
    })
    
    .declareMethod('updateAudioElementCurrentTime', function (time, max) {
      var gadget = this;
      // If there is no data in sourceBuffer return from here.
      if (gadget.params.sourceBuffer.buffered.length === 0) {
        return;
      }
      // If time is in range of buffered data, just update the current time of audio.
      if (time > gadget.params.sourceBuffer.buffered.start(0) && time < gadget.params.sourceBuffer.buffered.end(0)) {
         gadget.element.querySelector('audio').currentTime = time;
         return gadget.updateCurrentTime(time);
      }
      
      gadget.params.index = Math.floor((gadget.params.index / max) * time) - 1000;
      return new RSVP.Queue()
        .push(function () {
          gadget.params.sourceBuffer.abort();
          gadget.params.sourceBuffer.timestampOffset = time;
          gadget.params.sourceBuffer.remove(
            gadget.params.sourceBuffer.buffered.start(0),
            gadget.params.sourceBuffer.buffered.end(0)
          );
          return gadget.setUpdateEvent();
        })
        .push(function () {
          gadget.element.querySelector('audio').currentTime = time;
          return gadget.updateCurrentTime(time);
        });
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

    .declareMethod('setSourceBuffer', function () {
      this.params.sourceBuffer = this.params.mediaSource.addSourceBuffer('audio/mpeg');
      return RSVP.all([this.setUpdateEvent(), this.timeUpdate()]);
    })

    .declareMethod('setUpdateEvent', function () {
      var gadget = this;
      return gadget.getAudioChunk()
        .push(function (buffer) {
          if (buffer instanceof ArrayBuffer && !gadget.params.sourceBuffer.updating) {
            gadget.params.sourceBuffer.appendBuffer(buffer);
            return new RSVP.Queue()
              .push(function () {
                return promiseEventListener(gadget.params.sourceBuffer, 'updateend', false);
              })
              .push(function () {
                gadget.params.max_progress_time = gadget.params.max_progress_time > gadget.params.sourceBuffer.timestampOffset ?
                  gadget.params.max_progress_time : gadget.params.sourceBuffer.timestampOffset;
                return gadget.updateTotalTime(gadget.params.max_progress_time);
              });
          }
          if (buffer === undefined && gadget.params.mediaSource.readyState === 'open') {
            gadget.params.mediaSource.endOfStream();
          }
        });
    })

    .declareMethod('render', function (params) {
      var gadget = this,
        audio = this.element.querySelector('audio'),
        queue = new RSVP.Queue();
      gadget.params.id = params.id;
      gadget.params.name = params.name;
      gadget.params.end = false;
      gadget.params.index = 0;
      gadget.params.max_progress_time = 0;
      gadget.params.mediaSource = new MediaSource();
      
      audio.src = URL.createObjectURL(gadget.params.mediaSource);

      return queue
        .push(function () {
          return promiseEventListener(gadget.params.mediaSource, 'sourceopen', false);
        })
        .push(function () {
          if (!gadget.params.name) {
            return gadget.getSetting('hateoas_url');
          }
        })
        .push(function (hateoas_url) {
          if (!gadget.params.name) {
            gadget.params.name = hateoas_url + gadget.params.id;
          }
          return RSVP.all([
            gadget.setSourceBuffer(),
            gadget.configurePlayerContext()
          ]);
        });
    })

    .ready(function () {
      var audioContext = new AudioContext(),
        audio = this.element.querySelector('audio'),
        gain = audioContext.createGain(),
        source = audioContext.createMediaElementSource(audio);

      this.params = {
        audioContext: audioContext,
        gain: gain,
        source: source
      };
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('currentTime')) {
        return this.updateCurrentTime(modification_dict.currentTime);
      }
    })

    .declareJob('requestChunk', function () {
      var gadget = this;

      return gadget.getAudioChunk()
        .push(function (buffer) {
          gadget.params.requested = false;
          if (buffer instanceof ArrayBuffer && !gadget.params.sourceBuffer.updating) {
            return gadget.params.sourceBuffer.appendBuffer(buffer);
          }
          if (buffer === undefined && gadget.params.mediaSource.readyState === 'open') {
            gadget.params.mediaSource.endOfStream();
          }
        })
        .push(function () {
          return promiseEventListener( gadget.params.sourceBuffer, 'updateend', false);
        })
        .push(function () {
          gadget.params.max_progress_time = gadget.params.max_progress_time > gadget.params.sourceBuffer.timestampOffset ?
            gadget.params.max_progress_time : gadget.params.sourceBuffer.timestampOffset;
          return gadget.updateTotalTime(gadget.params.max_progress_time);
        });
    })

    .declareJob('timeUpdate', function () {
      var gadget = this,
        audio = gadget.element.querySelector('audio');

      return loopEventListener(
        audio,
        'timeupdate',
        false,
        function () {
          return new RSVP.Queue()
            .push(function () {
              if ((gadget.params.sourceBuffer.timestampOffset - audio.currentTime) < 10 &&
                  !gadget.params.requested) {
                gadget.params.requested = true;
                return gadget.requestChunk();
              }
            })
            .push(function () {
              return gadget.changeState({ currentTime: audio.currentTime });
            });
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this,
        audio = gadget.element.querySelector('audio');
      return new RSVP.Queue()
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
            gadget.params.source.disconnect(0);
            gadget.params.gain.disconnect(0);
            gadget.params.audioContext.close(); 
          } else {
            throw error;
          }
        });
    });
}(window, rJS, RSVP, AudioContext, URL, MediaSource, rJS.loopEventListener));