/*jslint indent: 2, unparam: true, bitwise: true */
/*global rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO,
         promiseEventListener, domsugar, createImageBitmap, FormData, Caman,
         FileReader, DataView, URL, fx*/
(function (rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO,
           promiseEventListener, domsugar, createImageBitmap, FormData, caman,
           FileReader, DataView, URL, fx) {
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

  function promiseCanvasToBlob(canvas, compression) {
    return new Promise(function (resolve) {
      // XXX too slow, takes 2 seconds or more on mobile.
      canvas.toBlob(resolve, 'image/jpeg', compression);
    });
  }

  function getOrientationFromArrayBuffer(array_buffer) {
    var view = new DataView(array_buffer),
      length = view.byteLength,
      offset = 2,
      marker,
      little,
      tags,
      i;

    if (view.getUint16(0, false) !== 0xFFD8) {
      return -2;
    }
    while (offset < length) {
      if (view.getUint16(offset + 2, false) <= 8) {
        return -1;
      }
      marker = view.getUint16(offset, false);
      offset += 2;
      if (marker === 0xFFE1) {
        offset += 2;
        if (view.getUint32(offset, false) !== 0x45786966) {
          return -1;
        }
        offset += 6;
        little = view.getUint16(offset, false) === 0x4949;
        offset += view.getUint32(offset + 4, little);
        tags = view.getUint16(offset, little);
        offset += 2;
        for (i = 0; i < tags; i = i + 1) {
          if (view.getUint16(offset + (i * 12), little) === 0x0112) {
            return view.getUint16(offset + (i * 12) + 8, little);
          }
        }
      } else if ((marker & 0xFF00) !== 0xFF00) {
        break;
      }
      offset += view.getUint16(offset, false);
    }
    return -1;
  }

  function getOrientation(blob) {
    return new RSVP.Queue(jIO.util.readBlobAsArrayBuffer(blob))
      .push(function (evt) {
        return getOrientationFromArrayBuffer(evt.target.result);
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

  function handleGfx(canvas, settings) {
    var webgl_canvas = fx.canvas(),
      texture = webgl_canvas.texture(canvas),
      tmp;

    // apply the ink filter
    tmp = webgl_canvas.draw(texture);

    if ((settings.brightness && settings.brightness !== 0) ||
        (settings.contrast && settings.contrast !== 0)) {
      tmp.brightnessContrast(
        (settings.brightness || 0) / 100,
        (settings.contrast || 0) / 100
      );
    }

    if (settings.enable_greyscale) {
      tmp.hueSaturation(0, -1);
    }
    tmp.update();
    return webgl_canvas;
  }

  function handleCaman(canvas, settings) {
    var local_caman;

    function canceller() {
      // It's weird but Caman stores a lot of data
      // in this variables. Please, double check before remove
      // this code
      local_caman.pixelData = null;
      local_caman.originalPixelData = null;
      local_caman.renderer.modPixelData = null;
      local_caman.imageData = null;
      local_caman.initializedPixelData = null;
      // Clear caman as much as possible
      local_caman = null;
      caman.Store.flush(true);
    }

    return new Promise(function (resolve, reject) {
      // XXX the correct usage is `new Caman()` but the library does not support it
      local_caman = caman(canvas, null, function () {
        try {
          if (settings.brightness && settings.brightness !== 0) {
            this.brightness(settings.brightness);
          }
          if (settings.contrast && settings.contrast !== 0) {
            this.contrast(settings.contrast);
          }
          if (settings.enable_greyscale) {
            this.greyscale();
          }
          this.render(function () {
            // XXX canceller should be called automatically ?
            canceller();
            resolve(canvas);
          });
        } catch (error) {
          canceller();
          reject(error);
        }
      });
      return local_caman;
    }, canceller);
  }

  function handleCropper(element, data, callback) {
    var cropper;

    function canceller() {
      cropper.destroy();
    }

    // creating Cropper is asynchronous
    return new RSVP.Promise(function (resolve, reject) {
      cropper = new Cropper(element, {
        // restrict the minimum canvas size to fit within the container
        viewMode: 2,
        guides: true,
        center: true,
        background: false,
        minContainerWidth: 1,
        minContainerHeight: 1,
        responsive: true,
        restore: true,
        // Avoid any cropper calculation or guessing
        scalable: false,
        rotatable: false,
        checkOrientation: false,
        zoomable: false,
        movable: false,
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
    return new RSVP.Queue()
      .push(function () {
        if (gadget.state['blob_url_' + blob_page] === undefined) {
          // Slow, takes 2 seconds or more on mobile.
          return new RSVP.Queue(
            promiseCanvasToBlob(gadget.state['blob_canvas_' + blob_page],
                                gadget.state.preferred_image_settings_data.compression || 1)
          )
            .push(function (blob) {
              return jIO.util.readBlobAsDataURL(blob);
            })
            .push(function (evt) {
              gadget.state['blob_url_' + blob_page] = evt.target.result;
            });
        }
      })
      .push(function () {
        var data = new FormData();
        data.append("input_value",
                    gadget.state['blob_url_' + blob_page].split(';')[1].split(',')[1]);
        data.append("active_process_url", gadget.state.active_process);
        return jIO.util.ajax({
          "type": "POST",
          "url": gadget.state.store_new_image_cropped_method,
          "data": data,
          "xhrFields": {
            withCredentials: true
          }
        });
      })
      .push(function (evt) {
        var state_dict = {};
        state_dict['blob_state_' + blob_page] = 'OK';
        state_dict['blob_uuid_' + blob_page] =
          JSON.parse(evt.target.responseText).uuid;
        return gadget.changeState(state_dict);
      }, function () {
        var state_dict = {};
        state_dict['blob_state_' + blob_page] = 'error';
        return gadget.changeState(state_dict);
      });
  }

  //////////////////////////////////////////////////
  // helper function
  //////////////////////////////////////////////////
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

  function selectMediaDevice(camera_list, current_device_id, force_new_device) {
    return getVideoDeviceList()
      .push(function (info_list) {
        var j,
          device,
          len = info_list.length;
        for (j = 0; j < len; j += 1) {
          device = info_list[j];
          if (device.kind === 'videoinput') {
            if (!current_device_id ||
                (camera_list.indexOf(device.deviceId) === -1 &&
                ((force_new_device && (device.deviceId !== current_device_id)) ||
                  (!force_new_device && (device.deviceId === current_device_id))))) {
              return device.deviceId;
            }
          }
        }

        if (len > 0) {
          return info_list[0].deviceId;
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
    gadget.detached_promise_dict[key] = new RSVP.Queue(promise)
      .push(undefined, function (error) {
        // Crash the gadget if the detached promise raise an unexpected error
        gadget.raise(error);
      });
  }

  function buildPreviousThumbnailDom(gadget) {
    var img_class,
      btn_class = "",
      len = gadget.state.page_count,
      thumbnail_dom_list = [];

    return gadget.getTranslationList(["New Page"])
      .push(function (result_list) {
        var key, el;
        for (el in gadget.state) {
          if (gadget.state.hasOwnProperty(el) && el.indexOf("blob_state_") !== -1) {
            key = parseInt(el.replace("blob_state_", ""), 10);
            if (gadget.state['blob_state_' + key] !== 'deleted') {
              if (gadget.state['blob_state_' + key] === "error") {
                img_class = "show-img upload-error";
              } else {
                img_class = "show-img";
              }

              if (gadget.state['blob_state_' + key] === "saving") {
                btn_class = "btn-thumbnail ui-btn-icon-top ui-icon-spinner";
              } else {
                btn_class = "btn-thumbnail";
              }
              thumbnail_dom_list.push(domsugar('button', {
                type: "button",
                "class": btn_class,
                // Do not allow to show again the current image
                // or do not allow to show saving image (to simplify button management)
                disabled: (key === gadget.state.page) || (gadget.state['blob_state_' + key] === 'saving')
              }, [domsugar("img", {"class": img_class,
                                   'data-page': key,
                                    src: gadget.state['blob_url_' + key]})]));
            }
          }
        }
        thumbnail_dom_list.push(domsugar('button', {type: 'button',
                                                    text: result_list[0],
                                                    // Do not allow to show again the current image
                                                    disabled: (len === gadget.state.page - 1),
                                                    "class": 'new-btn ui-btn-icon-left ui-icon-plus'
                                                   }));
        return domsugar('ol', {"class": "thumbnail-list"}, thumbnail_dom_list);
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
          gadget.getTranslationList(["Capture", "Change Camera", "Page", "Auto Crop"]),
          buildPreviousThumbnailDom(gadget)
        ]);
      })
      .push(function (result_list) {
        var button_list = [],
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
        button_list.push(domsugar('button', {
          type: 'button',
          'class': 'take-picture-btn ui-btn-icon-left ui-icon-circle',
          text: result_list[1][0]
        }));

        button_list.push(
          domsugar('button', {type: 'button',
                              'class': 'auto-crop-btn ui-icon-fast-forward ui-btn-icon-left',
                              text: result_list[1][3]
                             }));

        div = domsugar('div', {'class': 'camera'}, [
          domsugar('div', {'class': 'camera-header'}, [
            domsugar('h4', [
              result_list[1][2] + ' ',
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

  function fixPhotoOrientationSizeColor(blob, original_width, original_height,
                                        settings) {
    var orientation;
    return getOrientation(blob)
      .push(function (result) {
        orientation = result;

        var expected_width = settings.maximum_width,
          bitmap_options;
        // If orientation is correct, return the original blob
        // and size is small
        // and no color correction is expected
        if (((orientation < 2) || (8 < orientation)) &&
            ((!expected_width) ||
             ((original_width < expected_width) && (original_height < expected_width))) &&
            (!(settings.brightness || settings.contrast || settings.enable_greyscale))) {
          return blob;
        }

        // Else, transform the image
        return new RSVP.Queue(createImageBitmap(blob))

          .push(function (bitmap) {
            // Check if image dimension must be changed
            // It is mandatory to check the bitmap info,
            // as the image could be rotated
            var canvas,
              webgl_context,
              higher_dimension_key,
              higher_dimension_value;

            if (bitmap.width < bitmap.height) {
              higher_dimension_key = 'resizeHeight';
              higher_dimension_value = bitmap.height;
            } else {
              higher_dimension_key = 'resizeWidth';
              higher_dimension_value = bitmap.width;
            }

            canvas = document.createElement('canvas');
            webgl_context = canvas.getContext('webgl');

            expected_width = Math.min(
              expected_width || webgl_context.getParameter(webgl_context.MAX_TEXTURE_SIZE),
              webgl_context.getParameter(webgl_context.MAX_TEXTURE_SIZE) - 1
            );

            if ((!!expected_width) && (expected_width < higher_dimension_value)) {
              bitmap_options = {
                resizeQuality: 'high'
              };
              bitmap_options[higher_dimension_key] = expected_width;
              return createImageBitmap(blob, bitmap_options);
            }

            return bitmap;

          })
          .push(function (bitmap) {
            var height = bitmap.height,
              width = bitmap.width,
              canvas = domsugar('canvas'),
              ctx;

            // Caman expect the canvas to be in a container
            // in order to replace it when resizing
            domsugar('div', [canvas]);

            if ((4 < orientation) && (orientation < 9)) {
              canvas.width = height;
              canvas.height = width;
            } else {
              canvas.width = width;
              canvas.height = height;
            }

            ctx = canvas.getContext('2d');

            // transform context before drawing image
            switch (orientation) {
            case 2:
              ctx.transform(-1, 0, 0, 1, width, 0);
              break;
            case 3:
              ctx.transform(-1, 0, 0, -1, width, height);
              break;
            case 4:
              ctx.transform(1, 0, 0, -1, 0, height);
              break;
            case 5:
              ctx.transform(0, 1, 1, 0, 0, 0);
              break;
            case 6:
              ctx.transform(0, 1, -1, 0, height, 0);
              break;
            case 7:
              ctx.transform(0, -1, -1, 0, height, width);
              break;
            case 8:
              ctx.transform(0, -1, 1, 0, 0, width);
              break;
            default:
              break;
            }
            ctx.drawImage(bitmap, 0, 0);

            if (settings.brightness || settings.contrast || settings.enable_greyscale) {
              return handleGfx(canvas, settings);
              // return handleCaman(canvas, settings);
            }
            return canvas;
          })
          .push(function (final_canvas) {
            return promiseCanvasToBlob(final_canvas);
          });
      });
  }

  function createLoadedImgElement(url) {
    var img = domsugar('img', {src: url});
    return new RSVP.Queue(RSVP.any([
      promiseEventListener(img, 'load', false),
      // Crash if it fails to load
      new RSVP.Queue(promiseEventListener(img, 'error', false))
        .push(function () {
          throw new Error("Can't load the image src");
        })
    ]))
      .push(function () {
        return img;
      });
  }

  // Capture the media stream
  function captureAndRenderPicture(gadget, is_auto_crop) {
    var settings = gadget.state.preferred_image_settings_data,
      btn = gadget.element.querySelector(".take-picture-btn"),
      image_capture = new window.ImageCapture(
        gadget.element.querySelector('video').srcObject.getVideoTracks()[0]
      ),
      blob_url,
      original_width,
      original_height;

    // Display last video frame while doing calculation
    gadget.element.querySelector('video').pause();

    return new RSVP.Queue()
      .push(function () {
        btn.classList.remove("ui-icon-circle");
        btn.classList.add("ui-icon-spinner");
        return image_capture.getPhotoCapabilities();
      })
      .push(function (capabilities) {
        original_width = capabilities.imageWidth.max;
        original_height = capabilities.imageHeight.max;

        return image_capture.takePhoto({
          imageWidth: original_width,
          imageHeight: original_height
        });
      })
      .push(function (blob) {
        gadget.detached_promise_dict.media_stream.cancel('Not needed anymore, as captured');
        return fixPhotoOrientationSizeColor(blob, original_width,
                                            original_height, settings);
      })
      .push(function (blob) {
        blob_url = URL.createObjectURL(blob);
        return RSVP.all([
          gadget.getTranslationList(["Delete", "Save", "Page"]),
          createLoadedImgElement(blob_url),
          buildPreviousThumbnailDom(gadget)
        ]);
      })
      .push(function (result_list) {

        var img = result_list[1],
          div,
          defer = RSVP.defer(),
          edit_picture_element;

        if (!is_auto_crop) {
          edit_picture_element = domsugar('div', {'class': 'edit-picture'}, [
            domsugar('button', {type: 'button',
                                'class': 'reset-btn ui-btn-icon-left ui-icon-times',
                                text: result_list[0][0]
                               }),
            domsugar('button', {type: 'button',
                                'class': 'confirm-btn ui-btn-icon-left ui-icon-check',
                                text: result_list[0][1]
                               })
          ]);
        } else {
          // Keep the previous disabled button list
          // in order to reduce the flickering
          edit_picture_element = gadget.element.querySelector('.edit-picture');
        }

        // Prepare the cropper canvas
        div = domsugar('div', {'class': 'camera'}, [
          domsugar('div', {'class': 'camera-header'}, [
            domsugar('h4', [
              result_list[0][2] + ' ',
              domsugar('label', {'class': 'page-number', text: gadget.state.page})
            ])
          ]),
          // If you don't know what you are doing:
          // DON'T remove img from a div img-container.
          // DON'T replace img by canvas.
          domsugar("div", {"class": "img-container"}, [img]),
          edit_picture_element,
          result_list[2]
        ]);

        // XXX How to change the dom only when cropper is ready?
        // For now, it needs to access dom element size
        gadget.element.replaceChild(div, gadget.element.firstElementChild);
        btn.classList.add("ui-icon-circle");
        btn.classList.remove("ui-icon-spinner");
        addDetachedPromise(gadget, 'cropper',
                           handleCropper(img,
                                         gadget.state.preferred_cropped_canvas_data,
                                         defer.resolve));
        return defer.promise;
      })
      .push(function (cropper) {
        URL.revokeObjectURL(blob_url);
        gadget.cropper = cropper;
      });
  }

  function renderSubmittedPicture(gadget) {
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          gadget.getTranslationList(["Delete", "Save", "Page"]),
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

        if (gadget.state['blob_state_' + gadget.state.page] === 'error') {
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
              result_list[0][2] + ' ',
              domsugar('label', {'class': 'page-number', text: gadget.state.page + 1})
            ])
          ]),
          domsugar('div', {'class': 'img-container'}, [
            domsugar('img', {src: gadget.state['blob_url_' + gadget.state.page]})
          ]),
          // XXX TODO: why is the button rendering different from the other pages?
          domsugar('div', {'class': 'edit-picture'}, button_list),
          result_list[1]
        ]);

        // XXX How to change the dom only when cropper is ready?
        // For now, it needs to access dom element size
        gadget.element.replaceChild(div, gadget.element.firstElementChild);
        gadget.element.querySelector(".camera-header").scrollIntoView(false);
      });
  }

  function cropPicture(gadget) {
    var canvas = gadget.cropper.getCroppedCanvas(),
      state_dict;
    state_dict = {
      preferred_cropped_canvas_data: gadget.cropper.getData(),
      display_step: 'display_video',
      page: gadget.state.page + 1,
      page_count: gadget.state.page_count + 1
    };
    // Keep image date, as user may need to display it again
    state_dict['blob_canvas_' + gadget.state.page_count] = canvas;
    // state_dict['blob_url_' + gadget.state.page_count] = data_url;
    state_dict['blob_state_' + gadget.state.page_count] = 'saving';
    state_dict['blob_uuid_' + gadget.state.page_count] = null;

    return gadget.changeState(state_dict)
      .push(function () {
        // XXX Ensure that you have the active process relative url
        addDetachedPromise(gadget, 'ajax_' + (gadget.state.page_count - 1),
                           handleAsyncStore(gadget, gadget.state.page_count - 1));

        gadget.detached_promise_dict.cropper.cancel('Not needed anymore, as cropped');
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
      page_count: 0,
      camera_list: []
    })
    .declareMethod('render', function (options) {
      // This method is called during the ERP5 form rendering
      // changeState is used to ensure not resetting the gadget current display
      // if not needed
      var gadget = this,
        camera_list =  gadget.state.camera_list,
        default_value = JSON.parse(options.value);

      return selectMediaDevice(camera_list, gadget.state.device_id, false)
        .push(function (device_id) {
          if (camera_list.indexOf(device_id) === -1) {
            camera_list.push(device_id);
          }
          return gadget.changeState({
            store_new_image_cropped_method: options.store_new_image_cropped_method,
            active_process: default_value.active_process,
            image_list: default_value.image_list,
            camera_list: camera_list,
            preferred_cropped_canvas_data: JSON.parse(options.preferred_cropped_canvas_data),
            preferred_image_settings_data: JSON.parse(options.preferred_image_settings_data),
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
      if (display_step === 'auto_crop_picture') {
        return captureAndRenderPicture(gadget, true);
      }
      if (display_step === 'show_picture') {
        return renderSubmittedPicture(gadget);
      }

      if (display_step) {
        // Ease developper work by raising for not handled cases
        throw new Error('Unhandled display step: ' + gadget.state.display_step);
      }

      // Only refresh the thumbnail area
      // if display_step is not modified
      return buildPreviousThumbnailDom(gadget)
        .push(function (result) {
          thumbnail_container = gadget.element.querySelector('.thumbnail-list');
          thumbnail_container.parentElement.replaceChild(
            result,
            thumbnail_container
          );
        });
    })

    .onEvent("click", function (evt) {
      // Only handle click on BUTTON and IMG element
      var el,
        key,
        gadget = this,
        tag_name = evt.target.tagName,
        state_dict;

      if (tag_name !== 'BUTTON' &&
          (tag_name !== 'IMG' || evt.target.className.indexOf("show-img") === -1)) {
        return;
      }

      // Disable any button. It must be managed by this gadget
      evt.preventDefault();
      // If user clicks on same image twice,
      // we don't need to disable everything again if parent is already disabled
      if (tag_name === 'BUTTON' || (tag_name === 'IMG' && !evt.target.parentElement.disabled)) {
        gadget.element.querySelectorAll('button').forEach(function (elt) {
          elt.disabled = true;
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
          page: gadget.state.page + 1
        });
      }

      if (evt.target.className.indexOf("delete-btn") !== -1) {
        state_dict = {
          display_step: 'display_video',
          page: 0
        };

        for (el in gadget.state) {
          if (gadget.state.hasOwnProperty(el) && el.indexOf("blob_state_") !== -1) {
            key = el.replace("blob_state_", "");
            if (gadget.state['blob_state_' + key] !== 'deleted') {
              state_dict.page = state_dict.page + 1;
            }
          }
        }

        state_dict['blob_state_' + gadget.state.page] = 'deleted';
        return gadget.changeState(state_dict);
      }

      if (evt.target.className.indexOf("take-picture-btn") !== -1) {
        return gadget.changeState({
          display_step: 'crop_picture'
        });
      }

      if (evt.target.className.indexOf("confirm-btn") !== -1) {
        return cropPicture(gadget);
      }

      if (evt.target.className.indexOf("auto-crop-btn") !== -1) {
        return gadget.changeState({
          display_step: 'auto_crop_picture'
        })
          .push(function () {
            return cropPicture(gadget);
          });
      }

      if (evt.target.className.indexOf("retry-btn") !== -1) {
        // XXX Ensure that you have the active process relative url
        addDetachedPromise(gadget, 'ajax_' + (gadget.state.page),
                           handleAsyncStore(gadget, gadget.state.page));
        state_dict = {
          display_step: 'display_video',
          page: gadget.state.page_count + 1
        };
        state_dict['blob_state_' + gadget.state.page] = 'saving';
        return gadget.changeState(state_dict);
      }

      if (evt.target.className.indexOf("change-camera-btn") !== -1) {
        return selectMediaDevice(gadget.state.camera_list, gadget.state.device_id, true)
          .push(function (device_id) {
            var camera_list = gadget.state.camera_list;
            if (camera_list.indexOf(device_id) === -1) {
              camera_list.push(device_id);
            } else {
              camera_list = [device_id];
            }
            return gadget.changeState({
              display_step: 'display_video',
              preferred_cropped_canvas_data: {},
              camera_list: camera_list,
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
      var key,
        uuid_key,
        result,
        gadget = this,
        image_list = [];

      for (key in gadget.state) {
        if (gadget.state.hasOwnProperty(key)) {
          if (key.indexOf("blob_state_") !== -1 &&
              gadget.state[key] === "OK") {
            uuid_key = "blob_uuid_" + key.replace("blob_state_", "");
            image_list.push(gadget.state[uuid_key]);
          }
        }
      }
      result = {
        data_json: JSON.stringify({
          active_process: gadget.state.active_process,
          image_list: image_list,
          preferred_cropped_canvas_data: gadget.state.preferred_cropped_canvas_data
        })
      };
      return result;
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      var gadget = this,
        has_thumbnail = false,
        key;
      for (key in gadget.state) {
        if (gadget.state.hasOwnProperty(key)) {
          if (key.indexOf("blob_state_") !== -1 &&
              !gadget.state[key].match("deleted|OK")) {
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

}(rJS, RSVP, window, document, navigator, Cropper, Promise, JSON, jIO,
  promiseEventListener, domsugar, createImageBitmap, FormData, Caman,
  FileReader, DataView, URL, fx));