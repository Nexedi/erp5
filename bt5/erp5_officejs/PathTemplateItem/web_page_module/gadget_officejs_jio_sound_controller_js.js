/*global window, rJS, RSVP, jIO, AudioContext,
  URL, MediaSource, loopEventListener, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP, AudioContext, URL, MediaSource, loopEventListener, document) {
  "use strict";

  rJS(window)
    //////////////////////////////////////////////
    // Acquire methods
    /////////////////////////////////////////////
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('jio_getAttachment', 'jio_getAttachment')
    .declareAcquiredMethod('updateCurrentTime', 'updateCurrentTime')
    .declareAcquiredMethod('updateTotalTime', 'updateTotalTime')

    //////////////////////////////////////////////
    // Declare methods
    /////////////////////////////////////////////
    .declareMethod('configurePlayerContext', function () {
      this.source.connect(this.gain);
      this.gain.connect(this.audioContext.destination);
    })

    .declareMethod('getAudioChunk', function () {
      var gadget = this, start, end;
      start = gadget.index;
      if (start >= gadget.length) {
        return;
      }

      end = start + 10e5 >= gadget.length ? gadget.length - 1 : start + 10e5;
      // Call `getAttachment` method of jIO to fetch a chunk of data from IDB storage.
      return this.jio_getAttachment(this.id, 'data', { start: start, end: end })
        .push(function (blob) {
          gadget.index += 10e5;
          return RSVP.Queue().push(function () {
            return jIO.util.readBlobAsArrayBuffer(blob);
          }).push(function (evt) {
            return evt.target.result;
          });
        });
    })

    .declareMethod('handlePlayPause', function () {
      if (this.play) {
        // Audio player is in play condition.
        this.play = false;
        this.audio.pause();
      } else {
        // Audio player is in pause condition.
        this.play = true;
        this.audio.play();
      }
    })

    .declareMethod('handleSound', function () {
      if (this.audio.muted) {
        this.audio.muted = false;
      } else {
        this.audio.muted = true;
      }
    })

    .declareMethod('setSourceBuffer', function () {
      this.sourceBuffer = this.mediaSource.addSourceBuffer('audio/mpeg');
      return this.setUpdateEvent();
    })

    .declareMethod('setUpdateEvent', function () {
      var gadget = this;
      return gadget.getAudioChunk().push(function (buffer) {
        // gadget.mediaSource.removeBuffer(gadget.sourceBuffer);
        try {
          if (buffer) {
            gadget.sourceBuffer.appendBuffer(buffer);
          }
        } catch (ignore) {}
        if (gadget.replay) {
          gadget.audio.play();
          gadget.replay = false;
        }
      }).push(function () {
        return gadget.setUpdate();
      });
    })

    .declareJob('setUpdate', function () {
      var gadget = this;
      return loopEventListener(
        gadget.sourceBuffer,
        'updateend',
        false,
        function () {
          // `timestampOffset` value can give the time of the buffered audio data.
          if (gadget.sourceBuffer.timestampOffset < (gadget.count * 30)) {
            return gadget.getAudioChunk().push(function (buffer) {
              try {
                if (buffer) {
                  return gadget.sourceBuffer.appendBuffer(buffer);
                }
              } catch (ignore) {}
              if (!buffer && gadget.mediaSource.readyState === 'open') {
                return gadget.mediaSource.endOfStream();
              }
            });
          }
        },
        true
      );
    })

    .declareMethod('handleRangeRequest', function (index) {
      // We can also return from here without doing anything if the current
      // range is already present in the buffer.
      this.replay = true;
      this.count = 1;
      this.mediaSource = new MediaSource();
      this.audio.src =  URL.createObjectURL(this.mediaSource);
      this.index = index;
      this.mediaSource.onsourceopen = this.setSourceBuffer.bind(this);
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('render', function (params) {
      this.id = params.id;
      this.length = params.length;
      //this.duration = params.duration;
      this.index = 0;
      if (this.duration) {
        this.updateTotalTime(this.duration);
      }
      return this.configurePlayerContext();
    })

    .ready(function () {
      var audioContext = new AudioContext();
      this.audioContext = audioContext;
      this.play = false;
      this.count = 1;
      this.offset = 0;
      this.audio = document.querySelector('audio');
      this.gain = audioContext.createGain();
      this.source = audioContext.createMediaElementSource(this.audio);
      this.mediaSource = new MediaSource();
      this.audio.src =  URL.createObjectURL(this.mediaSource);
      this.mediaSource.onsourceopen = this.setSourceBuffer.bind(this);
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.audio,
        'timeupdate',
        false,
        function () {
          if (gadget.audio.currentTime > (gadget.count * 30) - 10) {
            gadget.count = gadget.count + 1;
            return gadget.getAudioChunk().push(function (buffer) {
              try {
                if (buffer) {
                  gadget.sourceBuffer.appendBuffer(buffer);
                }
              } catch (ignore) {}
            }).push(function () {
              gadget.currentTime = gadget.audio.currentTime + gadget.offset;
              gadget.currentTime = gadget.currentTime > gadget.duration ? gadget.duration : gadget.currentTime;
              var percentage = ((98 / gadget.duration) * gadget.currentTime);
              //gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (percentage + 1) + '%, #bcbcbc 0%';
              //gadget.element.querySelector('.playhead').style.marginLeft = percentage + '%';
              gadget.updateCurrentTime(gadget.currentTime);
            });
          }
          gadget.currentTime = gadget.audio.currentTime + gadget.offset;
          gadget.currentTime = gadget.currentTime > gadget.duration ? gadget.duration : gadget.currentTime;
          var percentage = ((98 / gadget.duration) * gadget.currentTime);
          //gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (percentage + 1) + '%, #bcbcbc 0%';
          //gadget.element.querySelector('.playhead').style.marginLeft = percentage + '%';
          gadget.updateCurrentTime(gadget.currentTime);
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return RSVP.Queue().push(function () {
        return loopEventListener(
          gadget.audio,
          'ended',
          false,
          function () {
            gadget.play = false;
            gadget.customPlayer.querySelector('.play-btn').classList.add('ui-icon-play');
            gadget.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-pause');
          },
          true
        );
      }).push(undefined, function () {
        // Pause when gadget go out of scope { CancellationError }.
        gadget.audio.pause();
        gadget.source.disconnect(0);
        gadget.gain.disconnect(0);
        gadget.audioContext.close();
      });
    });
/*
    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.timeline'),
        'mousemove',
        false,
        function (evt) {
          if (gadget.mousedown) {
            var val = ((evt.offsetX / gadget.element.querySelector('.timeline').offsetWidth)) * 100;
            val = (val > 98 ? 98 : val);
            gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (val + 1) + '%, #bcbcbc 0%';
            gadget.element.querySelector('.playhead').style.marginLeft = val + '%';
            gadget.currentTime = (val * gadget.duration) / 98;
            gadget.audio.currentTime = gadget.currentTime;
          }
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.timeline'),
        'click',
        false,
        function (evt) {
          var val, position;
          val = ((evt.offsetX / gadget.element.querySelector('.timeline').offsetWidth)) * 100;
          val = (val > 98 ? 98 : val);
          gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (val + 1) + '%, #bcbcbc 0%';
          gadget.element.querySelector('.playhead').style.marginLeft = val + '%';
          gadget.offset = (val * gadget.duration) / 98;
          position = Math.floor(((gadget.length / gadget.duration) * gadget.offset)) - 10e3;
          return gadget.handleRangeRequest(position);
        },
        true
      );
    })
*/
}(window, rJS, jIO, RSVP, AudioContext, URL, MediaSource, loopEventListener, document));