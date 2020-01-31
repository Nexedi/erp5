/*jslint indent: 2, unparam: true */
/*global rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar, createImageBitmap, FormData*/
(function (rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar, createImageBitmap, FormData) {
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

  function handleCropper(element, data, callback) {
    var cropper;

    function canceller() {
      cropper.destroy();
    }

    // creating Cropper is asynchronous
    return new RSVP.Promise(function (resolve, reject) {
      cropper = new Cropper(element, {
        data: data,
        ready: function () {
          return new RSVP.Queue()
            .push(function () {
              return callback(cropper);
            })
            .push(undefined, function (error) {
              if (!(error instanceof RSVP.CancellationError)) {
                canceller();
                reject(error);
              }
            });
        }
      });
    }, canceller);
  }

  function handleAsyncStore(gadget, blob_page) {
    var data = new FormData();
    data.append("input_value",
                     gadget.state['blob_url_' + blob_page].split(';')[1].split(',')[1]);
    data.append("active_process_url", gadget.state.active_process);
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          "type": "POST",
          "url": gadget.state.store_new_image_cropped_method,
          "data": data,
          "xhrFields": {
            withCredentials: true
          }
        });
      })
      .push(function () {
        var state_dict = {};
        state_dict['blob_state_' + blob_page] = 'OK';
        // XXX TODO: ajax must return a active process image content UUID
        // which should be sent in the final form submittion
        state_dict['blob_uuid_' + blob_page] = 'XXX';
        return gadget.changeState(state_dict);
      }, function () {
        // XXX TODO: Handle error case
        var state_dict = {};
        state_dict['blob_state_' + blob_page] = 'Error';
        return gadget.changeState(state_dict);
      });
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
    gadget.detached_promise_dict[key] = new RSVP.Queue()
      .push(function () {
        return promise;
      })
      .push(undefined, function (error) {
        // Crash the gadget if the detached promise raise an unexpected error
        gadget.raise(error);
      });
  }

  function buildPreviousThumbnailDom(gadget) {
    var i,
      len = gadget.state.page_count,
      thumbnail_dom_list = [];


    return gadget.getTranslationList(["Page", "New Page"])
      .push(function (result_list) {
        for (i = 0; i < len; i += 1) {
          // XXX TODO: show nice looking thumbnail
          // from gadget.state.blob_url_i
          // XXX TODO translation + right term
          // XXX TODO display a loader when sending
          if (gadget.state['blob_state_' + i] !== 'deleted') {
            thumbnail_dom_list.push(domsugar('button', {type: 'button',
                                                        text: result_list[0] + (i + 1) + ' (' + gadget.state['blob_state_' + i] + ')',
                                                        // Do not allow to show again the current image
                                                        // or do not allow to show sending image (to simplify button management)
                                                        disabled: (i === gadget.state.page) || (gadget.state['blob_state_' + i] === 'sending'),
                                                        'class': 'show-img',
                                                        'data-page': i
                                                      }));
          }
        }
        // Always add a button to generate a new image
        // XXX TODO translation + right term
        thumbnail_dom_list.push(domsugar('button', {type: 'button',
                                                    text: result_list[1],
                                                    // Do not allow to show again the current image
                                                    disabled: (len === gadget.state.page - 1),
                                                    'class': 'new-btn'
                                                 }));
        return domsugar('ol', thumbnail_dom_list);
      });
  }

  // Display the video stream from a media source
  function renderVideoCapture(gadget) {
    var video;
    return RSVP.Queue()
      .push(function () {
        var defer = RSVP.defer();
        addDetachedPromise(gadget, 'media_stream',
                           handleUserMedia(gadget.state.device_id, defer.resolve));
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
          gadget.getTranslationList(["Capture", "Change Camera"]),
          buildPreviousThumbnailDom(gadget)
        ]);
      })
      .push(function (result_list) {
        var button_list = [
          domsugar('button', {type: 'button',
                              'class': 'take-picture-btn ui-btn-icon-left ui-icon-circle',
                              text: result_list[1][0]
                             })
        ],
          div;
        // Only display the change camera if device has at least 2 cameras
        if (result_list[0].length > 1) {
          button_list.push(
            domsugar('button', {type: 'button',
                                'class': 'change-camera-btn ui-icon-refresh ui-btn-icon-left',
                                text: result_list[1][1]
                               })
          );
        }

        div = domsugar('div', {'class': 'camera'}, [
          domsugar('div', {'class': 'camera-header'}, [
            domsugar('h4', [
              'Page ',
              domsugar('label', {'class': 'page-number', text: gadget.state.page})
            ])
          ]),
          domsugar('div', {'class': 'camera-input'}, [video]),
          domsugar('div', {'class': 'edit-picture'}, button_list),
          result_list[2]
        ]);

        gadget.element.replaceChild(div, gadget.element.firstElementChild);

      });
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
          gadget.getTranslationList(["Delete", "Save"]),
          createImageBitmap(blob),
          buildPreviousThumbnailDom(gadget)
        ]);
      })
      .push(function (result_list) {
        var // blob_url = URL.createObjectURL(blob),
          // img = domsugar('img', {src: blob_url});
          bitmap = result_list[1],
          canvas = domsugar('canvas', {'class': 'canvas'}),
          defer = RSVP.defer();

        // Prepare the cropper canvas
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        canvas.getContext('2d').drawImage(bitmap, 0, 0);

        div = domsugar('div', {'class': 'camera'}, [
          domsugar('div', {'class': 'camera-header'}, [
            domsugar('h4', [
              'Page ',
              domsugar('label', {'class': 'page-number', text: gadget.state.page})
            ])
          ]),
          canvas,
          domsugar('div', {'class': 'edit-picture'}, [
            domsugar('button', {type: 'button',
                                'class': 'reset-btn ui-btn-icon-left ui-icon-times',
                                text: result_list[0][0]
                               }),
            domsugar('button', {type: 'button',
                                'class': 'confirm-btn ui-btn-icon-left ui-icon-check',
                                text: result_list[0][1]
                               })
          ]),
          result_list[2]
        ]);

        // XXX How to change the dom only when cropper is ready?
        // For now, it needs to access dom element size
        gadget.element.replaceChild(div, gadget.element.firstElementChild);

        addDetachedPromise(gadget, 'cropper',
                           handleCropper(canvas,
                                         gadget.state.preferred_cropped_canvas_data,
                                         defer.resolve));
        return defer.promise;
      })
      .push(function (cropper) {
        gadget.cropper = cropper;
      });
  }

  function renderSubmittedPicture(gadget) {
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          gadget.getTranslationList(["Delete", "Save"]),
          buildPreviousThumbnailDom(gadget)
        ]);
      })
      .push(function (result_list) {
        var button_list = [
          // XXX TODO: improve icon
          domsugar('button', {type: 'button',
                              'class': 'delete-btn ui-btn-icon-left ui-icon-times',
                              text: result_list[0][0]
                             })
        ],
          div;

        if (gadget.state['blob_state_' + gadget.state.page] === 'failed') {
          button_list.push(
            // XXX TODO improve icon
            domsugar('button', {type: 'button',
                                'class': 'retry-btn ui-btn-icon-left ui-icon-times',
                                text: result_list[0][1]
                               })
          );
        }

        div = domsugar('div', {'class': 'camera'}, [
          domsugar('div', {'class': 'camera-header'}, [
            domsugar('h4', [
              'Page ',
              domsugar('label', {'class': 'page-number', text: gadget.state.page + 1})
            ])
          ]),
          domsugar('img', {src: gadget.state['blob_url_' + gadget.state.page]}),
          // XXX TODO: why is the button rendering different from the other pages?
          domsugar('div', {'class': 'edit-picture'}, button_list),
          result_list[1]
        ]);

        // XXX How to change the dom only when cropper is ready?
        // For now, it needs to access dom element size
        gadget.element.replaceChild(div, gadget.element.firstElementChild);
      });
  }

  //////////////////////////////////////////////////
  // Gadget API
  //////////////////////////////////////////////////
  rJS(window)
    .ready(function () {
      this.detached_promise_dict = {};
    })
    .declareJob('raise', function (error) {
      throw error;
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
      display_step: 'display_video',
      page: 1,
      page_count: 0
    })
    .declareMethod('render', function (options) {
      // This method is called during the ERP5 form rendering
      // changeState is used to ensure not resetting the gadget current display
      // if not needed
      var gadget = this,
        default_value = JSON.parse(options.value);
      return selectMediaDevice(gadget.state.device_id, false)
        .push(function (device_id) {
          return gadget.changeState({
            dialog_method: options.dialog_method,
            store_new_image_cropped_method: options.store_new_image_cropped_method,
            active_process: default_value.active_process,
            image_list: default_value.image_list,
            preferred_cropped_canvas_data: JSON.parse(options.preferred_cropped_canvas_data),
            device_id: device_id,
            key: options.key,
            first_render: true
          });
        });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        display_step,
        thumbnail_container;
      // ALL DOM modifications must be done only in this method
      // this prevent concurrency issue on DOM access

      // Only refresh the full gadget content after the first render call
      // or if the display_step is modified
      // or if displaying another image
      if (modification_dict.first_render || modification_dict.hasOwnProperty('page')) {
        display_step = gadget.state.display_step;
      } else {
        display_step = modification_dict.display_step;
      }
      if (display_step === 'display_video' || modification_dict.hasOwnProperty('device_id')) {
        return renderVideoCapture(gadget);
      }
      if (display_step === 'crop_picture') {
        return captureAndRenderPicture(gadget);
      }
      if (display_step === 'show_picture') {
        return renderSubmittedPicture(gadget);
      }
      if (display_step) {
        // Ease developper work by raising for not handled cases
        throw new Error('Unhandled display step: ' + gadget.state.display_step);
      }

      // Only refresh the thumbnail list
      // if display_step is not modified
      // XXX TODO use a more precise selector
      return buildPreviousThumbnailDom(gadget)
        .push(function (result) {
          thumbnail_container = gadget.element.querySelector('ol');
          thumbnail_container.parentElement.replaceChild(
            result,
            thumbnail_container
          );
        });
    })

    .onEvent("click", function (evt) {
      // Only handle click on BUTTON element
      if (evt.target.tagName !== 'BUTTON') {
        return;
      }

      var gadget = this,
        state_dict;

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

      if (evt.target.className.indexOf("new-btn") !== -1) {
        return gadget.changeState({
          display_step: 'display_video',
          page: gadget.state.page_count + 1
        });
      }

      if (evt.target.className.indexOf("delete-btn") !== -1) {
        state_dict = {
          display_step: 'display_video',
          page: gadget.state.page_count + 1
        };
        state_dict['blob_state_' + gadget.state.page] = 'deleted';
        return gadget.changeState(state_dict);
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
            state_dict = {
              preferred_cropped_canvas_data: gadget.cropper.getData(),
              display_step: 'display_video',
              page: gadget.state.page + 1,
              page_count: gadget.state.page_count + 1
            };
            // Keep image date, as user may need to display it again
            state_dict['blob_url_' + gadget.state.page_count] = evt.target.result;
            state_dict['blob_state_' + gadget.state.page_count] = 'sending';
            return gadget.changeState(state_dict);
          })
          .push(function () {
            // XXX TODO Send the image to ERP5
            // XXX Ensure that you have the active process relative url
            addDetachedPromise(gadget, 'ajax_' + (gadget.state.page_count - 1),
                               handleAsyncStore(gadget, gadget.state.page_count - 1));

            gadget.detached_promise_dict.cropper.cancel('Not needed anymore, as cropped');
          });
      }

      if (evt.target.className.indexOf("retry-btn") !== -1) {
        // XXX TODO Send the image to ERP5
        // XXX Ensure that you have the active process relative url
        addDetachedPromise(gadget, 'ajax_' + (gadget.state.page),
                           handleAsyncStore(gadget, gadget.state.page));
        state_dict = {
          display_step: 'display_video',
          page: gadget.state.page_count + 1
        };
        state_dict['blob_state_' + gadget.state.page] = 'sending';
        return gadget.changeState(state_dict);
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

      if (evt.target.className.indexOf("show-img") !== -1) {
        if (gadget.detached_promise_dict.cropper) {
          gadget.detached_promise_dict.cropper.cancel('Not needed anymore, as cancelled');
        }
        if (gadget.detached_promise_dict.media_stream) {
          gadget.detached_promise_dict.media_stream.cancel('Not needed anymore, as cancelled');
        }

        return gadget.changeState({
          display_step: 'show_picture',
          page: parseInt(evt.target.getAttribute('data-page'), 10)
        });
      }

      throw new Error('Unhandled button: ' + evt.target.textContent);
    }, false, false)

    //////////////////////////////////////////////////
    // Used when submitting the form
    //////////////////////////////////////////////////
    .declareMethod('getContent', function () {
      var gadget = this,
        result = {};
      // XXX TODO: check all blob, and only return the UUID for the one in stored state
      result.data_json = JSON.stringify({
        active_process: gadget.state.active_process,
        image_list: gadget.state.image_list
      });
      result[gadget.state.key] = JSON.stringify({
        input_value: 'XXX',
        preferred_cropped_canvas_data: gadget.state.preferred_cropped_canvas_data
      });
      throw new Error('not implemented getContent');
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      var gadget = this,
        has_thumbnail = false,
        key;
      for (key in gadget.state) {
        if (gadget.state.hasOwnProperty(key)) {
          if (key.indexOf("blob_state_") !== -1 &&
              !gadget.state[key].match("deleted|stored")) {
            return false;
          }
          if (key.indexOf("blob_url_") !== -1) {
            if (!gadget.state[key]) {
              return false;
            }
            if (gadget.state[key] && !has_thumbnail) {
              has_thumbnail = true;
            }
          }
        }
      }
      return has_thumbnail;
    }, {mutex: 'changestate'})

    .declareAcquiredMethod("getTranslationList", "getTranslationList");

}(rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO, promiseEventListener, domsugar, createImageBitmap, FormData));