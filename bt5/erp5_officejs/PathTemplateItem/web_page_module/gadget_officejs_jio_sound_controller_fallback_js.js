/*global window, rJS, RSVP, URL, Blob
  loopEventListener, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO, URL, loopEventListener, document) {
  "use strict";

  rJS(window)
    //////////////////////////////////////////////
    // Acquire methods
    /////////////////////////////////////////////
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('jio_getAttachment', 'jio_getAttachment')
    .declareAcquiredMethod('togglePlayPause', 'togglePlayPause')
    .declareAcquiredMethod('toggleSound', 'toggleSound')
    .declareAcquiredMethod('updateCurrentTime', 'updateCurrentTime')
    .declareAcquiredMethod('updateTotalTime', 'updateTotalTime')

    //////////////////////////////////////////////
    // Declare methods
    /////////////////////////////////////////////
    .declareMethod('getAudioChunk', function () {
      var gadget = this,
        start,
        end,
        chunkLength;
      start = gadget.index;
      if (start >= gadget.length) {
        return;
      }
      chunkLength = gadget.length;
      end = chunkLength - 1;
      //end = start + chunkLength >= gadget.length ? gadget.length - 1 : start + chunkLength;
      // Call `getAttachment` method of jIO to fetch a chunk of data from IDB storage.
      try {
        // Check if attachment present in the store.
        throw this.jio_getAttachment(this.id, 'enclosure', { start: start, end: end });
      } catch (result) {
        return result.push(function (blob) {
          return blob;
        }).push(undefined, function (error) {
          return;
        });
      }
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

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('render', function (params) {
      var gadget = this;
      this.id = params.id;
      this.length = params.length;
      this.duration = params.duration;
      this.index = 0;
      if (this.duration) {
        this.updateTotalTime(this.duration);
      }
      if (this.id) {
        return this.getAudioChunk().push(function (blob) {
          if (!blob) {
            blob = new Blob(blob);
          }
          gadget.audio.src = URL.createObjectURL(blob);
        });
      }
    })

    .ready(function () {
      this.play = false;
      this.count = 1;
      this.offset = 0;
      this.customPlayer = this.element.querySelector('.audioplayer');
      this.audio = document.querySelector('audio');
      //document.body.appendChild(this.audio);
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.audio,
        'timeupdate',
        false,
        function () {
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
      });
    });
}(window, rJS, RSVP, jIO, URL, loopEventListener, document));