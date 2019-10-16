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
    dialogMethod,
    photo,
    photoInput,
    deviceId,
    imageCapture,
    pageNumber = 1,
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
    var start, end;
    return RSVP.Queue()
      .push(function () {
        return imageCapture.takePhoto({imageWidth: imageWidth});
      })
      .push(function (blob) {
        return readBlobAsDataURL(blob);
      })
      .push(function (result) {
        photo.setAttribute("src", result);
        photo.setAttribute("width", imageWidth);
        photo.setAttribute("height", imageHeight);
        photoInput.setAttribute("value", result.split(",")[1]);
        return drawCanvas(el, photo);
      });
  }

  function setPageOne(root) {
    root.querySelector(".page-number").innerText = pageNumber;
    root.querySelector(".reset-btn").style.display = "none";
    root.querySelector(".take-picture-btn").style.display = "inline-block";
    root.querySelector(".confirm-btn").style.display = "none";
    root.querySelector(".camera-input").style.display = "";
    if (cameraList.length > 1) {
      root.querySelector(".change-camera-btn").style.display = "inline-block";
    }
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

  function enableButton(root) {
    [".reset-btn", ".take-picture-btn",
     ".confirm-btn", ".change-camera-btn"].forEach(function (e) {
        root.querySelector(e).disabled = false;
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
        return setPageOne(root);
      });
  }

  function startup(root, device_id) {
    video = root.querySelector(".video");
    canvas = root.querySelector(".canvas");
    photo = root.querySelector("img");
    photoInput = root.querySelector(".photoInput");
    return handleUserMedia(root, device_id, gotStream);
  }

  rJS(window)
    .declareAcquiredMethod("customSubmitDialog", "customSubmitDialog")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareMethod('render', function (options) {
      var root;
      return this.getElement()
        .push(function (element) {
          root = element;
          pageNumber = 1;
          preferredCroppedCanvasData = preferredCroppedCanvasData || JSON.parse(
            options.preferred_cropped_canvas_data
          );
          dialogMethod = preferredCroppedCanvasData.dialog_method;
          // Clear photo input
          element.querySelector('.photoInput').value = "";
          if (deviceId) {
            root.querySelector(".camera-input").style.display = "";
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

          if (cameraList.length === 0) {
            for (j = 0; j < len; j += 1) {
              device = info_list[j];
              if (device.kind === 'videoinput') {
                cameraList.push(device);
              }
            }
          }
          if (cameraList.length >= 1) {
            // trick to select back camera in mobile
            deviceId = cameraList[cameraList.length - 1].deviceId;
          }

          if (deviceId) {
            return startup(root, deviceId);
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
    .onEvent("click", function (evt) {
      var root,
        newPreferredCroppedCanvasData,
        gadget = this;
      if (evt.target.name === "grayscale") {
        return this.getElement()
          .push(function () {
            return grayscale(canvas, photo);
          });
      }
      if (evt.target.className.indexOf("change-camera-btn") !== -1) {
        evt.preventDefault();
        for (var e in cameraList) {
          if (cameraList[e].deviceId !== deviceId) {
            deviceId = cameraList[e].deviceId;
            break;
          }
        }
        return gadget.getElement()
          .push(function (root) {
            return startup(root, deviceId);
          });
      }
      if (evt.target.className.indexOf("take-picture-btn") !== -1) {
        evt.preventDefault();
        return this.getElement()
          .push(function (el) {
            root = el;
            el.querySelector(".camera").style.maxWidth = video.offsetWidth + "px";
            el.querySelector(".camera-input").style.display = "none";
            return takePicture(el);
          })
          .push(function () {
            return setPageTwo(root);
          });
      }
      if (evt.target.className.indexOf("reset-btn") !== -1) {
        evt.preventDefault();
        return this.getElement()
          .push(function (el) {
            el.querySelector(".camera-input").style.display = "";
            el.querySelector(".camera-output").style.display = "none";
            cropper.destroy();
            return setPageOne(el);
          });
      }
      if (evt.target.className.indexOf("confirm-btn") !== -1) {
        evt.preventDefault();
        newPreferredCroppedCanvasData = cropper.getData();
        for (var p in newPreferredCroppedCanvasData) {
          if (newPreferredCroppedCanvasData.hasOwnProperty(p)) {
            preferredCroppedCanvasData[p] = newPreferredCroppedCanvasData[p];
          }
        }
        return this.getElement()
          .push(function (el) {
            root = el;
            disableButton(root);
            return cropper.getCroppedCanvas();
          })
          .push(function (canvas) {
            return new Promise(function (resolve, reject) {
              canvas.toBlob(function (blob) {
                resolve(blob);
              }, 'image/jpeg', 0.85);
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
            cropper.destroy();
          })
          .push(function () {
            return gadget.customSubmitDialog(dialogMethod);
          })
          .push(function () {
            enableButton(root);
            pageNumber = pageNumber + 1;
            return setPageOne(root);
          });
      }
    }, false, false);

}(rJS, RSVP, window, document, navigator, Cropper, console, FileReader, Promise, JSON));