/*global window, rJS, RSVP, jIO, AudioContext,
  URL, MediaSource, loopEventListener, document,
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
      if (gadget.params.end) {
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
                (error.target && error.target.result === undefined)) {
              return gadget.notifySubmitted({message: error.message || error.target.error, status: 'fail'});
            }
            throw error;
          });
        });
    })
    
    .declareMethod('updateAudioElementCurrentTime', function (time, max) {
      // If end already happen, just set the current time of audio element.
      this.params.max_progress_time = max;
      if (this.params.end) {
        this.element.querySelector('audio').currentTime = time;
        return;
      }

      var start,
        end,
        gadget = this,
        queue = new RSVP.Queue(),
        audio = gadget.element.querySelector('audio');

      gadget.params.index = Math.floor((this.params.index / max) * time) - 1000;
      gadget.params.time_offset = time;
      gadget.params.replay = true;
      gadget.params.mediaSource = new MediaSource();
      audio.src = URL.createObjectURL(gadget.params.mediaSource);

      return queue
        .push(function () {
          return gadget.updateCurrentTime(time);
        })
        .push(function() {
          return promiseEventListener(gadget.params.mediaSource, 'sourceopen', false);
        })
        .push(function() {
          return gadget.setSourceBuffer();
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
            gadget.params.sourceBuffer.onupdateend = function () {
              var total_time = this.params.sourceBuffer.timestampOffset + this.params.time_offset;
              total_time = total_time > this.params.max_progress_time ? total_time : this.params.max_progress_time;
              this.updateTotalTime(total_time);
            }.bind(gadget);
          }
          if (buffer === undefined && gadget.params.mediaSource.readyState === 'open') {
            gadget.params.mediaSource.endOfStream();
          }
          if (gadget.params.replay) {
            gadget.element.querySelector('audio').play();
            gadget.params.replay = false;
          }
        });
    })

    .declareMethod('render', function (params) {
      var gadget = this,
        queue = new RSVP.Queue();
      gadget.params.id = params.id;
      gadget.params.name = params.name;
      gadget.params.index = 0;
      gadget.params.max_progress_time = 0;
      gadget.params.time_offset = 0;
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
        source = audioContext.createMediaElementSource(audio),
        mediaSource = new MediaSource();

      audio.src =  URL.createObjectURL(mediaSource);
      this.params = {
        audioContext: audioContext,
        gain: gain,
        source: source,
        mediaSource: mediaSource
      };
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('currentTime')) {
        return this.updateCurrentTime(modification_dict.currentTime + this.params.time_offset);
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
          return gadget.changeState({ currentTime: gadget.element.querySelector('audio').currentTime });
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
          if ((gadget.params.sourceBuffer.timestampOffset - audio.currentTime) < 10 && !gadget.params.requested) {
            gadget.params.requested = true;
            return gadget.requestChunk();
          }
          return gadget.changeState({ currentTime: audio.currentTime });
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
}(window, rJS, RSVP, AudioContext, URL, MediaSource, loopEventListener));
