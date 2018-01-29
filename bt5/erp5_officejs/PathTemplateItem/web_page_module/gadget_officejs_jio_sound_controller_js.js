(function(window, rJS, jIO, RSVP, AudioContext, URL, MediaSource, loopEventListener, promiseEventListener, Promise) {
  "use strict";
  rJS(window)
    //////////////////////////////////////////////
    // Acquire methods
    //////////////////////////////////////////////
    .declareAcquiredMethod('getAttachment', 'getAttachment')

    //////////////////////////////////////////////
    // Declare methods
    /////////////////////////////////////////////
    .declareMethod('toHHMMSS', function(sec) {
      var sec_num = parseInt(sec, 10);
      var hours   = Math.floor(sec_num / 3600);
      var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
      var seconds = sec_num - (hours * 3600) - (minutes * 60);

      if (hours   < 10) {hours   = "0"+hours;}
      if (minutes < 10) {minutes = "0"+minutes;}
      if (seconds < 10) {seconds = "0"+seconds;}
      return hours+':'+minutes+':'+seconds;
    })
    .declareMethod('configurePlayerContext', function() {
      this.source.connect(this.gain);
      this.gain.connect(this.audioContext.destination);
    })
    .declareMethod('configurePlayer', function(id, name, length, duration) {
      // Configure player controller by setting the [id, title...] for the audio.
      var gadget = this;
      this.id = id;
      this.name = name;
      this.length = length;
      this.duration = duration;
      this.index = 0;
      if (this.duration) {
        this.toHHMMSS(this.duration).push(function (str) {
          gadget.element.querySelector('.total_time').innerHTML = str;
        });
      }
      return this.configurePlayerContext();
    })
    .declareMethod('getAudioChunk', function() {
      var gadget = this;
      var start, end;
      start = gadget.index;
      if (start >= gadget.length) {
        return RSVP.resolve(undefined);
      }
      end = start + 10e3 >= gadget.length ? gadget.length - 1 : start + 10e3;
      console.log(start, end);
      // Call `getAttachment` method of jIO to fetch a chunk of data from IDB storage.
      return this.getAttachment(this.id, this.name, {start: start, end: end})
        .push(function(blob) {
          gadget.index += 10e3;
          return RSVP.Queue().push(function() {
            return jIO.util.readBlobAsArrayBuffer(blob);
          }).push(function(evt) {
            return evt.target.result;
          });
        }).push(undefined, function(err) {
        throw err;
      });
    })
    .declareMethod('handlePlayPause', function() {
      var gadget = this;
      if (this.play) {
        // Audio player is in play condition.
        this.play = false;
        this.customPlayer.querySelector('.play-btn').classList.add('ui-icon-play');
        this.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-pause');
        this.audio.pause();
      } else {
        // Audio player is in pause condition.
        this.play = true;
        this.customPlayer.querySelector('.play-btn').classList.add('ui-icon-pause');
        this.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-play');
        this.audio.play();
      }
    })
    .declareMethod('handleSound', function() {
      if (this.audio.muted) {
        this.audio.muted = false;
        this.customPlayer.querySelector('.vol-btn').classList.remove('ui-icon-volume-off');
        this.customPlayer.querySelector('.vol-btn').classList.add('ui-icon-volume-up');
      } else {
        this.audio.muted = true;
        this.customPlayer.querySelector('.vol-btn').classList.remove('ui-icon-volume-up');
        this.customPlayer.querySelector('.vol-btn').classList.add('ui-icon-volume-off');
      }
    })
    .declareMethod('setSourceBuffer', function() {
      this.sourceBuffer = this.mediaSource.addSourceBuffer('audio/mpeg');
      return this.setUpdateEvent();
    })
    .ready(function() {
      var audioContext = this.audioContext = new AudioContext();
      var gadget = this;
      this.play = false;
      this.count = 1;
      this.offset = 0;
      this.lastOffset = 0;
      this.customPlayer = this.element.querySelector('.audioplayer');
      this.audio = this.element.querySelector('audio');
      this.gain = audioContext.createGain();
      this.analyser = audioContext.createAnalyser();
      this.filter = audioContext.createBiquadFilter();
      this.source = audioContext.createMediaElementSource(this.audio);
      this.mediaSource = new MediaSource();
      this.audio.src =  URL.createObjectURL(this.mediaSource);
      this.mediaSource.onsourceopen = this.setSourceBuffer.bind(this);
    })
  .declareMethod('setUpdateEvent', function() {
    var gadget = this;
    return gadget.getAudioChunk().push(function (buffer) {
      // gadget.mediaSource.removeBuffer(gadget.sourceBuffer);
      if (buffer) {
        gadget.sourceBuffer.appendBuffer(buffer);
      }
      if (gadget.replay) {
        gadget.audio.play();
        gadget.replay = false;
      }
      return loopEventListener(
        gadget.sourceBuffer,
        'updateend',
        false,
        function() {
          // `timestampOffset` value can give the time of the buffered audio data.
          // console.log(gadget.sourceBuffer.timestampOffset, (gadget.count * 30) - 10);
          if (gadget.sourceBuffer.timestampOffset < (gadget.count * 30)) {
            return gadget.getAudioChunk().push(function(buffer) {
              if (buffer) {
                return gadget.sourceBuffer.appendBuffer(buffer);
              }
              return gadget.mediaSource.endOfStream();
            });
          }
        },
        true
      );
    });
  })
  .declareMethod('createPromiseCapability', function() {
    var capability = {};
    capability.promise = new Promise(function(resolve, reject) {
      capability.resolve = resolve;
      capability.reject = reject;
    });
    return capability;
  })
  .declareMethod('handleRangeRequest', function(index) {
    // We can also return from here without doing anything if the current
    // range is already present in the buffer.
    this.replay = true;
    this.count = 1;
    this.mediaSource = new MediaSource();
    this.audio.src =  URL.createObjectURL(this.mediaSource);
    this.index = index;
    this.mediaSource.onsourceopen = this.setSourceBuffer.bind(this);
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.audio,
      'timeupdate',
      false,
      function() {
        if (gadget.audio.currentTime > (gadget.count * 30) - 10) {
          gadget.count++;
          gadget.getAudioChunk().push(function(buffer) {
            if (buffer) {
              gadget.sourceBuffer.appendBuffer(buffer);
            } else {
              gadget.mediaSource.endOfStream();
            }
          }).push(undefined, function(err) {
            throw err;
          });
        }
        gadget.currentTime = gadget.audio.currentTime + gadget.offset;
        gadget.currentTime = gadget.currentTime > gadget.duration ? gadget.duration : gadget.currentTime;
        var percentage = ((98 / gadget.duration) * gadget.currentTime);
        gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (percentage + 1) + '%, #bcbcbc 0%';
        gadget.element.querySelector('.playhead').style.marginLeft = percentage + '%';
        return gadget.toHHMMSS(gadget.currentTime).push(function (str) {
          return gadget.element.querySelector('.current_time').innerHTML = str;
        });
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    gadget.mousedown = false;
    return loopEventListener(
      gadget.element.querySelector('.playhead'),
      'mousedown',
      false,
      function () {
        gadget.mousedown = true;
        gadget.play = false;
        gadget.customPlayer.querySelector('.play-btn').classList.add('ui-icon-play');
        gadget.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-pause');
        gadget.audio.pause();
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    gadget.mousedown = false;
    return loopEventListener(
      gadget.element.querySelector('.timeline'),
      'mouseup',
      false,
      function () {
        gadget.mousedown = false;
        gadget.play = true;
        gadget.customPlayer.querySelector('.play-btn').classList.add('ui-icon-pause');
        gadget.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-play');
        gadget.audio.play();
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.element.querySelector('.timeline'),
      'mousemove',
      false,
      function (evt) {
        if (gadget.mousedown) {
          var val = (((evt.clientX - gadget.element.querySelector('.timeline').offsetLeft) / gadget.element.querySelector('.timeline').offsetWidth)) * 100;
          val = (val > 98 ? 98 : val);
          gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (val + 1) + '%, #bcbcbc 0%';
          gadget.element.querySelector('.playhead').style.marginLeft = val + '%';
          gadget.currentTime = (val * gadget.duration) / 98;
          gadget.audio.currentTime = gadget.currentTime;
          //var position = Math.floor(((gadget.length / gadget.duration) * gadget.currentTime)) - 1000;
          //return gadget.setUpdateEvent().push(function () {
            //gadget.audio.load();
            //return gadget.audio.play();
          //});
        }
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.element.querySelector('.timeline'),
      'click',
      false,
      function (evt) {
        var val = (((evt.clientX - gadget.element.querySelector('.timeline').offsetLeft) / gadget.element.querySelector('.timeline').offsetWidth)) * 100;
        val = (val > 98 ? 98 : val);
        gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (val + 1) + '%, #bcbcbc 0%';
        gadget.element.querySelector('.playhead').style.marginLeft = val + '%';
        gadget.lastOffset = gadget.offset;
        gadget.offset = (val * gadget.duration) / 98;
        var position = Math.floor(((gadget.length / gadget.duration) * gadget.offset)) - 10e3;
        return gadget.handleRangeRequest(position);
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.element.querySelector('.pVolumn'),
      'mouseover',
      false,
      function() {
        gadget.element.querySelector('.volTimeline').style.display = /*change it to block*/'none';
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.element.querySelector('.pVolumn'),
      'mouseleave',
      false,
      function() {
        gadget.element.querySelector('.volTimeline').style.display = 'none';
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.element.querySelector('.volTimeline'),
      'mouseover',
      false,
      function() {
        gadget.element.querySelector('.volTimeline').style.display = 'block';
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.element.querySelector('.volTimeline'),
      'mouseleave',
      false,
      function() {
        gadget.element.querySelector('.volTimeline').style.display = 'none';
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.audio,
      'ended',
      false,
      function() {
        gadget.play = false;
        gadget.customPlayer.querySelector('.play-btn').classList.add('ui-icon-play');
        gadget.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-pause');
      },
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.element.querySelector('.play-btn'),
      'click',
      false,
      gadget.handlePlayPause.bind(gadget),
      true
    );
  })
  .declareService(function() {
    var gadget = this;
    return loopEventListener(
      gadget.element.querySelector('.vol-btn'),
      'click',
      false,
      gadget.handleSound.bind(gadget),
      true
    );
  });
})(window, rJS, jIO, RSVP, AudioContext, URL, MediaSource, loopEventListener, promiseEventListener, Promise);