/*jslint indent: 2, unparam: true */
/*global rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar*/
(function (rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar) {
  "use strict";

  //////////////////////////////////////////////////
  // Browser API to promise
  //////////////////////////////////////////////////
  function promiseUserMedia(device_id) {
    return navigator.mediaDevices.getUserMedia({
      video: {
        deviceId: {
          exact: device_id
        }
      },
      audio: false
    });
  }

  function handleUserMedia(device_id, callback) {
    // Do not modify this function!
    // There is no need to add the gadget logic inside
    var stream;

    function canceller() {
      if (stream !== undefined) {
        // Stop the streams
        stream.getTracks().forEach(function (track) {
          track.stop();
        });
      }
    }

    function waitForStream(resolve, reject) {
      new RSVP.Queue()
        .push(function () {
          return promiseUserMedia(device_id);
        })
        .push(function (result) {
          stream = result;
          return callback(stream);
        })
        .push(undefined, function (error) {
          if (!(error instanceof RSVP.CancellationError)) {
            canceller();
            reject(error);
          }
        });
    }
    return new RSVP.Promise(waitForStream, canceller);
  }

  //////////////////////////////////////////////////
  // helper function
  //////////////////////////////////////////////////
  function selectMediaDevice(current_device_id, force_new_device) {
    if (!navigator.mediaDevices) {
      throw new Error("mediaDevices is not supported");
    }

    return new RSVP.Queue()
      .push(function () {
        return navigator.mediaDevices.enumerateDevices();
      })
      .push(function (info_list) {
        var j,
          device,
          len = info_list.length;

        for (j = len - 1; j >= 0; j -= 1) {
          // trick to select back camera in mobile
          device = info_list[j];
          if (device.kind === 'videoinput') {
            if ((!current_device_id) ||
                (force_new_device && (device.deviceId !== current_device_id)) ||
                (device.deviceId === current_device_id)) {
              return device.deviceId;
            }
          }
        }
        throw new Error("no media found");
      });
  }

  //////////////////////////////////////////////////
  // Private gadget function
  //////////////////////////////////////////////////
  function addDetachedPromise(gadget, key, promise) {
    // XXX TODO Handle error
    if (gadget.detached_promise_dict.hasOwnProperty(key)) {
      gadget.detached_promise_dict[key].cancel('Replacing key: ' + key);
    }
    gadget.detached_promise_dict[key] = promise;
  }

  // Display the video stream from a media source
  function renderVideoCapture(gadget) {
    var video;
    return RSVP.Queue()
      .push(function () {
        var defer = RSVP.defer();
        addDetachedPromise(gadget, 'media_stream',
                           handleUserMedia(gadget.state.device_id,
                                           defer.resolve));
        return defer.promise;
      })
      .push(function (media_stream) {
        video = document.createElement('video');
        video.srcObject = media_stream;
        video.autoplay = "autoplay";
        video.loop = "loop";
        video.muted = "muted";

        return RSVP.any([
          // Wait for the video to be ready
          promiseEventListener(video, 'loadedmetadata', true),
          promiseEventListener(video, 'canplaythrough', true),
          promiseEventListener(video, 'error', true, function () {
            throw new Error("Can't play the video file");
          })
        ]);
      })

      .push(function () {
        video.play();
        return gadget.getTranslationList([
          "Take Picture", "Change Camera"
        ]);
      })
      .push(function (translation_list) {
        var div = domsugar('div', {class: 'camera'}, [
          domsugar('div', {class: 'camera-header'}, [
            domsugar('h4', [
              'Page ',
              domsugar('label', {class: 'page-number', text: '1'})
            ])
          ]),
          domsugar('div', {class: 'camera-input'}, [video]),
          domsugar('div', {class: 'edit-picture'}, [
            domsugar('button', {type: 'button',
                                class: 'take-picture-btn ui-btn-icon-left ui-icon-circle',
                                text: translation_list[0]
                               }),
            domsugar('button', {type: 'button',
                                class: 'change-camera-btn ui-icon-refresh ui-btn-icon-left',
                                text: translation_list[1]
                               })
          ])
        ]);

        gadget.element.replaceChild(div, gadget.element.firstElementChild);

      });

/*
      .push(function () {
        var preferred_cropped_canvas_data = gadget.props.preferred_cropped_canvas_data;
        preferred_cropped_canvas_data = preferred_cropped_canvas_data || JSON.parse(gadget.state.preferred_cropped_canvas_data);
        // Clear photo input
        root.querySelector('.photoInput').value = "";
        gadget.props.page_number = parseInt(root.querySelector('input[name="page-number"]').value, 10);
        root.querySelector(".camera-input").style.display = "";
        root.querySelector(".camera-output").style.display = "none";


        gadget.props.preferred_cropped_canvas_data = preferred_cropped_canvas_data;
      })

      */
  }

  // Capture the media stream
  function captureAndRenderPicture(gadget) {
    var image_capture = new window.ImageCapture(
      gadget.element.querySelector('video').srcObject.getVideoTracks()[0]
    );
    return new RSVP.Queue()
      .push(function () {
        return image_capture.getPhotoCapabilities();
      })
      .push(function (capabilities) {
        return image_capture.takePhoto({imageWidth: capabilities.imageWidth.max});
      })
      .push(function (blob) {
        gadget.detached_promise_dict.media_stream.cancel('Not needed anymore, as captured');
        return createImageBitmap(blob);
      })
      .push(function (bitmap) {
        var // blob_url = URL.createObjectURL(blob),
          // img = domsugar('img', {src: blob_url}),
          canvas = domsugar('canvas', {class: 'canvas'});

        // Prepare the cropper canvas
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        canvas.getContext('2d').drawImage(bitmap, 0, 0);//, img.width, img.height);

        var div = domsugar('div', {class: 'camera'}, [
          domsugar('div', {class: 'camera-header'}, [
            domsugar('h4', [
              'Page ',
              domsugar('label', {class: 'page-number', text: '1'})
            ])
          ]),
          canvas,
          /*
          domsugar('div', {class: 'camera-input'}, [video]),
          */
          domsugar('div', {class: 'edit-picture'}, [
            domsugar('button', {type: 'button',
                                class: 'reset-btn ui-btn-icon-left ui-icon-times',
                                text: 'Reset'
                               }),
            domsugar('button', {type: 'button',
                                class: 'confirm-btn ui-btn-icon-left ui-icon-check',
                                text: 'Confirm'
                               })
          ])
        ]);

        gadget.element.replaceChild(div, gadget.element.firstElementChild);
        // creating Cropper is asynchronous
        return new RSVP.Promise(function (resolve) {
          gadget.cropper = new Cropper(canvas, {
            // data: gadget.props.preferred_cropped_canvas_data,
            ready: resolve
          });
        });
      });
/*
        return jIO.util.readBlobAsDataURL(blob);
      })
      .push(function (result) {
        var photoInput = el.querySelector(".photoInput"),
          photo = el.querySelector("img"),
          data_str = result.target.result;

        photo.setAttribute("src", data_str);
        photoInput.setAttribute("value", data_str.split(",")[1]);
        return drawCanvas(gadget, photo);
      });
  function drawCanvas(gadget, img) {
    var ratio, x, y,
      root = gadget.element,
      canvas = root.querySelector("canvas");
    canvas.width = gadget.props.image_width;
    canvas.height = gadget.props.image_height;
    ratio  = Math.min(canvas.width / img.width, canvas.height / img.height);
    x = (canvas.width - img.width * ratio) / 2;
    y = (canvas.height - img.height * ratio) / 2;

    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height, x, y, img.width * ratio, img.height * ratio);

    //contrastImage(canvas, canvas, 10);

    root.querySelector(".camera-output").style.display = "";
    if (gadget.props.cropper) {
      gadget.props.cropper.destroy();
    }
    // creating Cropper is asynchronous
    return new RSVP.Promise(function (resolve) {
      gadget.props.cropper = new Cropper(root.querySelector('.photo'), {
        data: gadget.props.preferred_cropped_canvas_data,
        ready: resolve
      });
    });
  }
  */
  }

  //////////////////////////////////////////////////
  // Gadget API
  //////////////////////////////////////////////////
  rJS(window)
    .ready(function () {
      this.detached_promise_dict = {};
    })
    .declareService(function handleDetachedPromiseDict() {
      // This service is responsable to cancel all ongoing detached promises
      // if the gadget is removed from the page
      var gadget = this;
      return new RSVP.Promise(function () {return; }, function canceller(msg) {
        var key;
        for (key in gadget.detached_promise_dict) {
          if (gadget.detached_promise_dict.hasOwnProperty(key)) {
            gadget.detached_promise_dict[key].cancel(msg);
          }
        }
      });
    })

    .declareMethod('render', function (options) {
      // This method is called during the ERP5 form rendering
      // changeState is used to ensure not resetting the gadget current display
      // if not needed
      var gadget = this;
      return selectMediaDevice(gadget.state.device_id, false)
        .push(function (device_id) {
          return gadget.changeState({
            dialog_method: options.dialog_method,
            preferred_cropped_canvas_data: options.preferred_cropped_canvas_data,
            display_step: 'display_video',
            device_id: device_id
            // XXX timestamp: new Date(),
          });
        });
    })

    .onStateChange(function () {
      var gadget = this;
      // ALL DOM modifications must be done only in this method
      // this prevent concurrency issue on DOM access

      /* The list of possible display_step are:
         * start_video: no button can be display at this step,
                        as it will not be possible to capture the stream yet
         * start_video: capture, stop the stream
         * reset: XXX
         * upload: XXX
      */
      if (gadget.state.display_step === 'display_video') {
        return renderVideoCapture(gadget);
      }

      if (gadget.state.display_step === 'crop_picture') {
        return captureAndRenderPicture(gadget);
      }

/*
      if (gadget.state.display_step === 'reset') {
        gadget.element.querySelector(".camera-input").style.display = "";
        gadget.element.querySelector(".camera-output").style.display = "none";
        gadget.element.querySelector('.photoInput').value = "";
        gadget.props.cropper.destroy();
        setPageOne(gadget);
        return gadget.deferChangeState({display_step: 'start_video'});
      }

      if (gadget.state.display_step === 'upload') {
        var e,
          new_preferred_cropped_canvas_data,
          camera_list = this.props.camera_list,
          root = this.element;
        new_preferred_cropped_canvas_data = gadget.props.cropper.getData();
        for (e in new_preferred_cropped_canvas_data) {
          if (new_preferred_cropped_canvas_data.hasOwnProperty(e)) {
            gadget.props.preferred_cropped_canvas_data[e] = new_preferred_cropped_canvas_data[e];
          }
        }
        return new RSVP.Queue()
          .push(function () {
            var canvas = gadget.props.cropper.getCroppedCanvas();
            disableButton(gadget.element);
            return new Promise(function (resolve) {
              canvas.toBlob(resolve, 'image/jpeg', 0.85);
            });
          })
          .push(function (blob) {
            return jIO.util.readBlobAsDataURL(blob);
          })
          .push(function (result) {
            var base64data = result.target.result,
              block = base64data.split(";"),
              realData = block[1].split(",")[1];
            root.querySelector(".photo").src = base64data;
            root.querySelector(".photoInput").value = realData;
            gadget.props.cropper.destroy();
          })
          .push(function () {
            return gadget.submitDialogWithCustomDialogMethod(gadget.state.dialog_method);
          })
          .push(function () {
            gadget.props.page_number = gadget.props.page_number + 1;
            root.querySelector('input[name="page-number"]').value = gadget.props.page_number;
          });
      }
      */
      // Ease developper work by raising for not handled cases
      throw new Error('Unhandled display step: ' + gadget.state.display_step);

    })

    .onEvent("click", function (evt) {
      var i,
        list;
      // Only handle click on BUTTON element
      if (evt.target.tagName !== 'BUTTON') {
        return;
      }

      // Disable any button. It must be managed by this gadget
      evt.preventDefault();
      list = this.element.querySelectorAll('button').forEach(function (elt) {
        elt.disabled = true;
      });

      if (evt.target.className.indexOf("take-picture-btn") !== -1) {
        return this.changeState({
          display_step: 'crop_picture'
        });
      }

      if (evt.target.className.indexOf("reset-btn") !== -1) {
        return this.changeState({
          display_step: 'display_video'
        });
      }
    /*
      if (evt.target.className.indexOf("confirm-btn") !== -1) {
        return this.changeState({
          display_step: 'upload'
        });
      }
*/

/*
      var e,
        new_preferred_cropped_canvas_data,
        gadget = this,
        camera_list = this.props.camera_list,
        root = this.element;

      *if (evt.target.name === "grayscale") {
        return grayscale(root.querySelector(".canvas"),
                         root.querySelector('.photo'));
      }*
      if (evt.target.className.indexOf("change-camera-btn") !== -1) {
        evt.preventDefault();

        for (e in camera_list) {
          if (camera_list.hasOwnProperty(e)) {
            if (camera_list[e].deviceId !== gadget.props.device_id) {
              gadget.props.device_id = camera_list[e].deviceId;
              break;
            }
          }
        }
        return gadget.startStream();
      }
*/
      throw new Error('Unhandled button: ' + evt.target.textContent);
    }, false, false)


    .declareAcquiredMethod(
      "submitDialogWithCustomDialogMethod",
      "submitDialogWithCustomDialogMethod"
    )
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted");

}(rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar));