/*jslint indent: 2, unparam: true */
/*global rJS, RSVP, window, navigator, Cropper, Promise, JSON, jIO, promiseEventListener*/
(function (rJS, RSVP, window, navigator, Cropper, Promise, JSON, jIO, promiseEventListener) {
  "use strict";

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

  function takePicture(gadget) {
    var el = gadget.element,
      image_capture = gadget.props.image_capture;
    return new RSVP.Queue()
      .push(function () {
        return image_capture.takePhoto({imageWidth: gadget.props.image_width});
      })
      .push(function (blob) {
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
  }

  function enableButton(root) {
    [".reset-btn", ".take-picture-btn",
      ".confirm-btn", ".change-camera-btn"].forEach(function (e) {
      root.querySelector(e).disabled = false;
    });
  }

  function setPageOne(gadget) {
    var root = gadget.element;
    root.querySelector(".page-number").innerText = gadget.props.page_number;
    root.querySelector(".reset-btn").style.display = "none";
    root.querySelector(".take-picture-btn").style.display = "inline-block";
    root.querySelector(".confirm-btn").style.display = "none";
    root.querySelector(".camera-input").style.display = "";
    if (gadget.props.camera_list.length > 1) {
      root.querySelector(".change-camera-btn").style.display = "inline-block";
    }
    return enableButton(root);
  }

  function setPageTwo(root) {
    root.querySelector(".reset-btn").style.display = "inline-block";
    root.querySelector(".confirm-btn").style.display = "inline-block";
    root.querySelector(".take-picture-btn").style.display = "none";
    root.querySelector(".camera-input").style.display = "none";
    root.querySelector(".camera-output").style.display = "";
    root.querySelector(".change-camera-btn").style.display = "none";
  }

  function disableButton(root) {
    [".reset-btn", ".take-picture-btn",
       ".confirm-btn", ".change-camera-btn"].forEach(function (e) {
      root.querySelector(e).disabled = true;
    });
  }

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

  function gotStream(media_stream) {
    var gadget = this;
    return new RSVP.Queue()
      .push(function () {
        var video = gadget.props.video;
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
        gadget.props.video.play();
        var image_capture;
        image_capture = new window.ImageCapture(media_stream.getVideoTracks()[0]);
        gadget.props.image_capture = image_capture;
        return image_capture.getPhotoCapabilities();
      })
      .push(function (photoCapabilities) {
        gadget.props.image_width = photoCapabilities.imageWidth.max;
        gadget.props.image_height = photoCapabilities.imageHeight.max;
      })
      .push(function () {
        return setPageOne(gadget);
      });
  }

  rJS(window)
    .declareAcquiredMethod(
      "submitDialogWithCustomDialogMethod",
      "submitDialogWithCustomDialogMethod"
    )
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .declareJob("startStream", function () {
      return handleUserMedia(this.props.device_id, gotStream.bind(this));
    })

    .ready(function () {
      this.props = {
        video: this.element.querySelector(".video")
      };
    })

    .declareMethod('render', function (options) {
      // This method is called during the ERP5 form rendering
      return this.changeState({
        dialog_method: options.dialog_method,
        preferred_cropped_canvas_data: options.preferred_cropped_canvas_data,
        // XXX to drop
        timestamp: new Date()
      });
    })

    .onStateChange(function () {
      var root = this.element,
        camera_list = [],
        gadget = this;

      return this.getTranslationList(["Webcam is not available", "Reset", "Take Picture", "Confirm", "Edit", "Change Camera"])
        .push(function (result_list) {
          var i,
            button_list = root.querySelectorAll("button");
          for (i = 0; i < button_list.length; i += 1) {
            button_list[i].innerText = " " + result_list[i + 1];
          }
          root.querySelector("video").innerText = result_list[0];
        })
        .push(function () {
          var preferred_cropped_canvas_data = gadget.props.preferred_cropped_canvas_data;
          preferred_cropped_canvas_data = preferred_cropped_canvas_data || JSON.parse(gadget.state.preferred_cropped_canvas_data);
          // Clear photo input
          root.querySelector('.photoInput').value = "";
          gadget.props.page_number = parseInt(root.querySelector('input[name="page-number"]').value, 10);
          root.querySelector(".camera-input").style.display = "";
          root.querySelector(".camera-output").style.display = "none";

          if (!navigator.mediaDevices) {
            throw ("mediaDevices is not supported");
          }
          gadget.props.preferred_cropped_canvas_data = preferred_cropped_canvas_data;
          return navigator.mediaDevices.enumerateDevices();
        })
        .push(function (info_list) {
          var j,
            device,
            len = info_list.length;

          if (camera_list.length === 0) {
            for (j = 0; j < len; j += 1) {
              device = info_list[j];
              if (device.kind === 'videoinput') {
                camera_list.push(device);
              }
            }
          }
          if (camera_list.length >= 1) {
            // trick to select back camera in mobile
            gadget.props.device_id = camera_list[camera_list.length - 1].deviceId;
          }
          gadget.props.camera_list = camera_list;
          return gadget.startStream();
        });
    })
    .declareMethod('getContent', function () {
      var input = this.element.querySelector('.photoInput'),
        result = {};

      result.field_your_document_scanner_gadget = JSON.stringify({
        "input_value": input.value,
        "preferred_cropped_canvas_data": this.props.preferred_cropped_canvas_data
      });
      return result;
    })
    .onEvent("click", function (evt) {
      var e,
        new_preferred_cropped_canvas_data,
        gadget = this,
        camera_list = this.props.camera_list,
        root = this.element;

      /*if (evt.target.name === "grayscale") {
        return grayscale(root.querySelector(".canvas"),
                         root.querySelector('.photo'));
      }*/
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
      if (evt.target.className.indexOf("take-picture-btn") !== -1) {
        evt.preventDefault();
        return new RSVP.Queue()
          .push(function () {
            disableButton(root);
            root.querySelector(".camera").style.maxWidth = gadget.props.video.offsetWidth + "px";
            return takePicture(gadget);
          })
          .push(function () {
            root.querySelector(".camera-input").style.display = "none";
            setPageTwo(root);
            return enableButton(root);
          });
      }
      if (evt.target.className.indexOf("reset-btn") !== -1) {
        evt.preventDefault();
        root.querySelector(".camera-input").style.display = "";
        root.querySelector(".camera-output").style.display = "none";
        root.querySelector('.photoInput').value = "";
        gadget.props.cropper.destroy();
        return setPageOne(gadget);
      }
      if (evt.target.className.indexOf("confirm-btn") !== -1) {
        evt.preventDefault();
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
    }, false, false);

}(rJS, RSVP, window, navigator, Cropper, Promise, JSON, jIO, promiseEventListener));