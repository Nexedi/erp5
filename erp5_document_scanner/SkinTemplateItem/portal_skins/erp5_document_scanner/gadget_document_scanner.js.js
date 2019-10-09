/*jslint indent: 2 */
/*global rJS, RSVP, window, document, navigator, Cropper, console, FileReader, Promise, JSON*/
(function (rJS, RSVP, window, document, navigator, Cropper, console, FileReader, Promise, JSON) {
  "use strict";

  var imageWidth,
    preferredCroppedCanvasData,
    imageHeight,
    cropper,
    video,
    stream,
    canvas,
    photo,
    photoInput,
    cameraSelected,
    imageCapture,
    cameraList = [];

  function readBlobAsDataURL(blob) {
    var fr = new FileReader();
    return new RSVP.Promise(function waitFormDataURLRead(resolve, reject) {
      fr.addEventListener("load", function handleDataURLRead(evt) {
        resolve(evt.target.result);
      });
      fr.addEventListener("error", reject);
      fr.readAsDataURL(blob);
    }, function cancelReadBlobAsDataURL() {
      fr.abort();
    });
  }

  function takePicture(el) {
    return RSVP.Queue()
      .push(function () {
        return imageCapture.takePhoto({imageWidth: imageWidth});
      })
      .push(function (blob) {
        return readBlobAsDataURL(blob);
      })
      .push(function (result) {
        photoInput.setAttribute("value", result.split(",")[1]);
        photo.setAttribute("src", result);
        photo.setAttribute("width", imageWidth);
        photo.setAttribute("height", imageHeight);
        el.querySelector(".capture-button").style.display = "";
        return drawCanvas(el, photo);
      });
  }

  function drawCanvas(gadget, img) {
    var ratio, x, y;
    canvas.width = imageWidth;
    canvas.height = imageHeight;
    ratio  = Math.min(canvas.width / img.width, canvas.height / img.height);
    x = (canvas.width - img.width * ratio) / 2;
    y = (canvas.height - img.height * ratio) / 2;

    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height, x, y, img.width * ratio, img.height * ratio);

    //contrastImage(canvas, canvas, 10);

    gadget.querySelector(".camera-output").style.display = "";
    if (cropper) {
      cropper.destroy();
    }
    return RSVP.Queue()
      .push(function () {
        cropper = new Cropper(
          gadget.querySelector('.photo'),
          {
            data: preferredCroppedCanvasData
          }
        );
      });
  }

  function contrastImage(input, output, contrast) {
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
  }

  function grayscale(input, output) {
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
    return RSVP.Queue()
      .push(function () {
        cropper = new Cropper(
          output,
          {
            data: preferredCroppedCanvasData
          }
        );
      });
  }

  function handleUserMedia(root, device_id, callback) {

    function canceller() {
      if (stream !== undefined) {
        // Stop the streams
        stream.getTracks().forEach(function (track) {
          track.stop();
        });
      }
    }

    function waitForStream() {
      new RSVP.Queue()
        .push(function () {
          return navigator.mediaDevices.getUserMedia({video: {deviceId: {exact: device_id}}});
        })
        .push(function (result) {
          stream = result;
          return callback(root, stream);
        })
        .push(undefined, function (error) {
          if (!(error instanceof RSVP.CancellationError)) {
            canceller();
          }
        });
    }

    return new RSVP.Promise(waitForStream, canceller);
  }

  function gotStream(root, mediaStream) {
    return RSVP.Queue()
      .push(function () {
        imageCapture = new window.ImageCapture(mediaStream.getVideoTracks()[0]);
        video.srcObject = mediaStream;
        return imageCapture.getPhotoCapabilities();
      })
      .push(function (photoCapabilities) {
        imageWidth = photoCapabilities.imageWidth.max;
        imageHeight = photoCapabilities.imageHeight.max;
        return video.play();
      })
      .push(function () {
        root.querySelector(".camera-input").style.display = "";
      });
  }

  function startup(root, device_id) {
    video = root.querySelector(".video");
    canvas = root.querySelector(".canvas");
    photo = root.querySelector(".photo");
    photoInput = root.querySelector(".photoInput");
    return handleUserMedia(root, device_id, gotStream);
  }

  function clearphoto() {
    var data, context = canvas.getContext("2d");
    context.fillRect(0, 0, canvas.width, canvas.height);

    data = canvas.toDataURL("image/png");
    photo.setAttribute("src", data);
  }

  rJS(window)
    .declareMethod('render', function (options) {
      var el,
        root;
      return this.getElement()
        .push(function (element) {
          root = element;
          preferredCroppedCanvasData = preferredCroppedCanvasData || JSON.parse(
            options.preferred_cropped_canvas_data
          );
          // Clear photo input
          element.querySelector('.photoInput').value = "";
          if (video) {
            video.pause();
          }
          if (cameraSelected) {
            root.querySelector(".camera-input").style.display = "";
            root.querySelector(".capture-button").style.display = "";
            root.querySelector(".camera-output").style.display = "none";
          }
          if (!navigator.mediaDevices) {
            throw ("mediaDevices is not supported");
          }
          return navigator.mediaDevices.enumerateDevices();
        })
        .push(function (info_list) {
          var j,
            device,
            len = info_list.length;
          for (j = 0; j < len; j += 1) {
            device = info_list[j];
            if (device.kind === 'videoinput') {
              cameraList.push(device);
            }
          }
          if (cameraList.length >= 1) {
            // trick to select back camera in mobile
            return startup(root, cameraList[cameraList.length - 1].deviceId);
          }
        });
    })
    .declareMethod('getContent', function () {
      var input = this.element.querySelector('.photoInput'),
        result = {};
      result.field_your_document_scanner_gadget = JSON.stringify({
        "input_value": input.value,
        "preferred_cropped_canvas_data": preferredCroppedCanvasData
      });
      return result;
    })
    /*.onEvent("change", function (evt) {
      if (evt.target.type === "select-one") {
        return this.getElement()
          .push(function (root) {
            var display;
            if (stream !== undefined) {
              // Stop the streams
              stream.getTracks().forEach(function (track) {
                track.stop();
              });
            }
            if (!evt.target.value) {
              display = "none";
            } else {
              display = "";
            }
            root.querySelector(".camera-input").style.display = display;
            if (evt.target.value) {
              return startup(root, evt.target.value);
            }
          });
      }
    }, false, true)*/

    .onEvent("click", function (evt) {
      var gadget, canvasData;
      if (evt.target.name === "grayscale") {
        return this.getElement()
          .push(function () {
            return grayscale(canvas, photo);
          });
      }
      if (evt.target.className === "startbutton") {
        evt.preventDefault();
        return this.getElement()
          .push(function (el) {
            el.querySelector(".camera-input").style.display = "none";
            return takePicture(el);
          });
      }
      if (evt.target.className === "reset-button") {
        evt.preventDefault();
        return this.getElement()
          .push(function (el) {
            el.querySelector(".camera-input").style.display = "";
            el.querySelector(".camera-output").style.display = "none";
            cropper.destroy();
            return startup(el, el.querySelector("select"));
          });
      }
      if (evt.target.className === "capture-button") {
        evt.preventDefault();
        preferredCroppedCanvasData = cropper.getData();
        canvasData = cropper.getCanvasData();
        return this.getElement()
          .push(function (el) {
            gadget = el;
            return cropper.getCroppedCanvas();
          })
          .push(function (canvas) {
            return new Promise(function (resolve, reject) {
              canvas.toBlob(function (blob) {
                resolve(blob);
              });
            });
          })
          .push(function (blob) {
            return readBlobAsDataURL(blob);
          })
          .push(function (data_url) {
            var base64data = data_url,
              block = base64data.split(";"),
              realData = block[1].split(",")[1];

            photo.src = base64data;
            photoInput.value = realData;
            gadget.querySelector(".camera-input").style.display = "none";
            gadget.querySelector(".camera-output").style.display = "";
            gadget.querySelector(".capture-button").style.display = "none";
            cropper.destroy();
          });
      }
    }, false, false);

}(rJS, RSVP, window, document, navigator, Cropper, console, FileReader, Promise, JSON));