/*jslint indent: 2 */
/*global rJS, RSVP, window, document, navigator, Cropper, console, FileReader, Promise, JSON*/
(function (rJS, RSVP, window, document, navigator, Cropper, console, FileReader, Promise, JSON) {
  "use strict";

  var imageWidth,
    preferredCroppedCanvasData,
    imageHeight,
    cropper,
    video,
    canvas,
    photo,
    photoInput,
    imageCapture;

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

  function takePicture(gadget) {
    imageCapture.takePhoto({imageWidth: imageWidth})
      .then(function (blob) {
        var reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = function () {
          photoInput.setAttribute("value", reader.result.split(",")[1]);
          photo.setAttribute("src", reader.result);
          photo.setAttribute("width", imageWidth);
          photo.setAttribute("height", imageHeight);
          return drawCanvas(gadget, photo);
        };
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

    //grayscale(canvas, canvas);
    //contrastImage(canvas, canvas, 10);

    gadget.querySelector(".camera-output").style.display = "";
    if (cropper) {
      cropper.destroy();
    }
    return RSVP.Queue()
      .push(function (data) {
        cropper = new Cropper(
          gadget.querySelector('.photo'), {data: preferredCroppedCanvasData});
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
    outputContext = output.getContext("2d");
    outputContext.putImageData(imageData, 0, 0);
  }

  function handleUserMedia(device_id, callback) {
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
          return navigator.mediaDevices.getUserMedia({video: {deviceId: {exact: device_id}}});
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

  function gotStream(mediaStream) {
    return RSVP.Queue()
      .push(function () {
        imageCapture = new window.ImageCapture(mediaStream.getVideoTracks()[0]);
        video.srcObject = mediaStream;
        return imageCapture.getPhotoCapabilities();
      })
      .push(function (photoCapabilities) {
        imageWidth = photoCapabilities.imageWidth.max;
        imageHeight = photoCapabilities.imageHeight.max;
        video.play();
      });
  }

  function startup(gadget, device_id) {
    video = gadget.querySelector(".video");
    canvas = gadget.querySelector(".canvas");
    photo = gadget.querySelector(".photo");
    photoInput = gadget.querySelector(".photoInput");

    return handleUserMedia(device_id, gotStream);
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
        root,
        selector;
      return this.getElement()
        .push(function (element) {
          root = element;
          selector = element.querySelector("select");
          preferredCroppedCanvasData = preferredCroppedCanvasData || JSON.parse(
            options.preferred_cropped_canvas_data);
          if (!selector.value && video) {
            video.pause();
          }
          if (selector.value) {
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
          if (root.querySelector("select").length > 1) {
            return;
          }
          for (j = 0; j < len; j += 1) {
            device = info_list[j];
            if (device.kind === 'videoinput') {
              el = document.createElement("option");
              el.value = device.deviceId;
              el.innerText = device.label;
              selector.appendChild(el);
            }
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
    .onEvent("change", function (evt) {
      if (evt.target.type === "select-one") {
        return this.getElement()
          .push(function (root) {
            if (!evt.target.value && video) {
              video.pause();
            }
            root.querySelector(".camera-input").style.display = "";
            if (evt.target.value) {
              return startup(root, evt.target.value);
            }
          });
      }
    }, false, true)

    .onEvent("click", function (evt) {
      var gadget, canvasData;
      if (evt.target.className === "startbutton") {
        return this.getElement()
          .push(function (el) {
            el.querySelector(".camera-input").style.display = "none";
            return takePicture(el);
          });
      }
      if (evt.target.className === "capture-button") {
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

            photo.style.width = canvasData.width + "px";
            photo.style.height = canvasData.height + "px";

            photo.src = base64data;
            photoInput.value = realData;
            gadget.querySelector(".capture-button").style.display = "none";
            cropper.destroy();
          });
      }
    }, false, true);

}(rJS, RSVP, window, document, navigator, Cropper, console, FileReader, Promise, JSON));