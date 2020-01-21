/*jslint indent: 2, unparam: true */
/*global rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar, createImageBitmap*/
(function (rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar, createImageBitmap) {
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
  /*function contrastImage(input, output, contrast) {
    var i,
      outputContext,
      inputContext = input.getContext("2d"),
      imageData = inputContext.getImageData(0, 0, input.width, input.height),
      data = imageData.data,
      factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
    for (i = 0; i < data.length; i += 4) {
      data[i] = factor * (data[i] - 128) + 128;
      data[i + 1] = factor * (data[i + 1] - 128) + 128;
      data[i + 2] = factor * (data[i + 2] - 128) + 128;
    }
    outputContext = output.getContext("2d");
    outputContext.putImageData(imageData, 0, 0);
  }*/

  /*function grayscale(input, output) {
    var i,
      gray,
      outputContext,
      outputCanvas = document.createElement("canvas"),
      inputContext = input.getContext("2d"),
      imageData = inputContext.getImageData(0, 0, input.width, input.height),
      data = imageData.data,
      arraylength = input.width * input.height * 4;
    //gray = 0.3*R + 0.59*G + 0.11*B
    // http://www.tannerhelland.com/3643/grayscale-image-algorithm-vb6/
    for (i = arraylength - 1; i > 0; i -= 4) {
      gray = 0.3 * data[i - 3] + 0.59 * data[i - 2] + 0.11 * data[i - 1];
      data[i - 3] = gray;
      data[i - 2] = gray;
      data[i - 1] = gray;
    }
    outputContext = outputCanvas.getContext("2d");
    outputContext.putImageData(imageData, 0, 0);
    data = canvas.toDataURL("image/png");
    output.setAttribute("src", data);
    if (cropper) {
      cropper.destroy();
    }
    return new RSVP.Queue()
      .push(function () {
        cropper = new Cropper(
          output,
          {
            data: preferred_cropped_canvas_data
          }
        );
      });
  }*/

  function getVideoDeviceList() {
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
          len = info_list.length,
          device_list = [];

        for (j = len - 1; j >= 0; j -= 1) {
          // trick to select back camera in mobile
          device = info_list[j];
          if (device.kind === 'videoinput') {
            device_list.push(device);
          }
        }
        return device_list;
      });
  }

  function selectMediaDevice(current_device_id, force_new_device) {
    return getVideoDeviceList()
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
                (!force_new_device && (device.deviceId === current_device_id))) {
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
        return RSVP.all([
          getVideoDeviceList(),
          gadget.getTranslationList(["Take Picture", "Change Camera"])
        ]);
      })
      .push(function (result_list) {
        var button_list = [
          domsugar('button', {type: 'button',
                              class: 'take-picture-btn ui-btn-icon-left ui-icon-circle',
                              text: result_list[1][0]
                             })
        ],
          div;
        // Only display the change camera if device has at least 2 cameras
        if (result_list[0].length > 1) {
          button_list.push(
            domsugar('button', {type: 'button',
                                class: 'change-camera-btn ui-icon-refresh ui-btn-icon-left',
                                text: result_list[1][1]
                               })
          );
        }

        div = domsugar('div', {class: 'camera'}, [
          domsugar('div', {class: 'camera-header'}, [
            domsugar('h4', [
              'Page ',
              domsugar('label', {class: 'page-number', text: '1'})
            ])
          ]),
          domsugar('div', {class: 'camera-input'}, [video]),
          domsugar('div', {class: 'edit-picture'}, button_list)
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
    ),
      div;
    return new RSVP.Queue()
      .push(function () {
        return image_capture.getPhotoCapabilities();
      })
      .push(function (capabilities) {
        return image_capture.takePhoto({imageWidth: capabilities.imageWidth.max});
      })
      .push(function (blob) {
        gadget.detached_promise_dict.media_stream.cancel('Not needed anymore, as captured');
        return RSVP.all([
          gadget.getTranslationList(["Reset", "Confirm"]),
          createImageBitmap(blob)
        ]);
      })
      .push(function (result_list) {
        var // blob_url = URL.createObjectURL(blob),
          // img = domsugar('img', {src: blob_url});
          bitmap = result_list[1],
          canvas = domsugar('canvas', {class: 'canvas'});

        // Prepare the cropper canvas
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        canvas.getContext('2d').drawImage(bitmap, 0, 0);

        div = domsugar('div', {class: 'camera'}, [
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
                                text: result_list[0][0]
                               }),
            domsugar('button', {type: 'button',
                                class: 'confirm-btn ui-btn-icon-left ui-icon-check',
                                text: result_list[0][1]
                               })
          ])
        ]);

        // XXX How to change the dom only when cropper is ready?
        // For now, it needs to access dom element size
        gadget.element.replaceChild(div, gadget.element.firstElementChild);

        // creating Cropper is asynchronous
        return new RSVP.Promise(function (resolve) {
          gadget.cropper = new Cropper(canvas, {
            data: gadget.state.preferred_cropped_canvas_data,
            ready: resolve
          });
        });
      });
  }

  function renderSubmittedPicture(gadget) {
    var div = domsugar('div', {class: 'camera'}, [
      domsugar('div', {class: 'camera-header'}, [
        domsugar('h4', [
          'Page ',
          domsugar('label', {class: 'page-number', text: '1'})
        ])
      ]),
      domsugar('img', {src: gadget.state.blob_url})
    ]);

    // XXX How to change the dom only when cropper is ready?
    // For now, it needs to access dom element size
    gadget.element.replaceChild(div, gadget.element.firstElementChild);
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

    .setState({
      display_step: 'display_video'
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
            preferred_cropped_canvas_data: JSON.parse(options.preferred_cropped_canvas_data),
            device_id: device_id,
            key: options.key
          });
        });
    })

    .onStateChange(function () {
      var gadget = this;
      // ALL DOM modifications must be done only in this method
      // this prevent concurrency issue on DOM access
      if (gadget.state.display_step === 'display_video') {
        return renderVideoCapture(gadget);
      }

      if (gadget.state.display_step === 'crop_picture') {
        return captureAndRenderPicture(gadget);
      }

      if (gadget.state.display_step === 'submitting') {
        return renderSubmittedPicture(gadget);
      }

      // Ease developper work by raising for not handled cases
      throw new Error('Unhandled display step: ' + gadget.state.display_step);

    })

    .declareMethod('getContent', function () {
      var gadget = this,
        result = {};
      if (gadget.state.display_step === 'submitting') {
        result[gadget.state.key] = JSON.stringify({
          input_value: gadget.state.blob_url.split(';')[1].split(',')[1],
          preferred_cropped_canvas_data: gadget.state.preferred_cropped_canvas_data
        });
      }
      return result;
    })

    .onEvent("click", function (evt) {
      // Only handle click on BUTTON element
      if (evt.target.tagName !== 'BUTTON') {
        return;
      }

      var gadget = this;

      // Disable any button. It must be managed by this gadget
      evt.preventDefault();
      gadget.element.querySelectorAll('button').forEach(function (elt) {
        elt.disabled = true;
      });

      if (evt.target.className.indexOf("take-picture-btn") !== -1) {
        return gadget.changeState({
          display_step: 'crop_picture'
        });
      }

      if (evt.target.className.indexOf("reset-btn") !== -1) {
        return gadget.changeState({
          display_step: 'display_video'
        });
      }

      if (evt.target.className.indexOf("confirm-btn") !== -1) {
        return new RSVP.Queue()
          .push(function () {
            var canvas = gadget.cropper.getCroppedCanvas();
            return new Promise(function (resolve) {
              canvas.toBlob(resolve, 'image/jpeg', 0.85);
            });
          })
          .push(function (blob) {
            return jIO.util.readBlobAsDataURL(blob);
          })
          .push(function (evt) {
            return gadget.changeState({
              blob_url: evt.target.result,
              preferred_cropped_canvas_data: gadget.cropper.getData(),
              display_step: 'submitting'
            });
          })
          .push(function () {
            return gadget.submitDialogWithCustomDialogMethod(gadget.state.dialog_method);
          })
          .push(function (evt) {
            return gadget.changeState({
              blob_url: undefined,
              display_step: 'display_video'
            });
          });
      }

      if (evt.target.className.indexOf("change-camera-btn") !== -1) {
        return selectMediaDevice(gadget.state.device_id, true)
          .push(function (device_id) {
            return gadget.changeState({
              display_step: 'display_video',
              device_id: device_id
            });
          });
      }

      throw new Error('Unhandled button: ' + evt.target.textContent);
    }, false, false)


    .declareAcquiredMethod(
      "submitDialogWithCustomDialogMethod",
      "submitDialogWithCustomDialogMethod"
    )
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted");

}(rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar, createImageBitmap));