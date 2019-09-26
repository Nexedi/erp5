/*jslint indent: 2 */
/*global rJS, RSVP, window, document, navigator, Cropper, console, FileReader, jIO, Promise*/
(function (rJS, RSVP, window, document, navigator, Cropper, console, FileReader, jIO, Promise) {
  "use strict";

  var imageWidth,
    imageHeight,
    cropper,
    video,
    canvas,
    photo,
    startbutton,
    photoInput,
    storage,
    imageCapture;

  function gotStream(mediaStream) {
    imageCapture = new window.ImageCapture(mediaStream.getVideoTracks()[0]);
    video.srcObject = mediaStream;
    return imageCapture.getPhotoCapabilities();
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

    document.querySelector("textarea[name='field_your_description']").value += "\nImage size " + img.width + "x" + img.height;

    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height, x, y, img.width * ratio, img.height * ratio);

    //grayscale(canvas, canvas);
    //contrastImage(canvas, canvas, 10);

    gadget.querySelector(".camera-output").style.display = "";
    if (cropper) {
      cropper.destroy();
    }
    return RSVP.Queue()
      .push(function () {
        return storage.get("settings");
      })
      .push(function (data) {
        cropper = new Cropper(gadget.querySelector('.photo'), {data: data});
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

  function startup(gadget, device_id) {
    video = gadget.querySelector(".video");
    canvas = gadget.querySelector(".canvas");
    photo = gadget.querySelector(".photo");
    photoInput = gadget.querySelector(".photoInput");
    startbutton = gadget.querySelector(".startbutton");

    return RSVP.Queue()
      .push(function () {
        return navigator.mediaDevices.getUserMedia({video: {deviceId: {exact: device_id}}});
      })
      .push(gotStream)
      .push(function (photoCapabilities) {
        imageWidth = photoCapabilities.imageWidth.max;
        imageHeight = photoCapabilities.imageHeight.max;
        document.querySelector("textarea[name='field_your_description']").value = "Max => " + imageWidth + "x" + imageHeight;
        video.play();
      });
  }

  function clearphoto() {
    var data, context = canvas.getContext("2d");
    context.fillRect(0, 0, canvas.width, canvas.height);

    data = canvas.toDataURL("image/png");
    photo.setAttribute("src", data);
  }

  rJS(window)
    .ready(function () {
      return RSVP.Queue()
        .push(function () {
          return jIO.createJIO({
            "type": "indexeddb",
            "database": "cropper_settings"
          });
        })
        .push(function (proxy) {
          storage = proxy;
          return storage.get("settings");
        })
        .then(undefined, function () {
          return storage.put("settings");
        });
    })
    .declareMethod('render', function () {
      var el,
        root,
        selector;
      return this.getElement()
        .push(function (element) {
          root = element;
          selector = element.querySelector("select");
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
      result.field_your_document_scanner_gadget = input.value;
      return result;
    })
    .onEvent("change", function (evt) {
      if (evt.target.type == "select-one") {
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
      if (evt.target.className == "startbutton") {
        return this.getElement()
          .push(function (el) {
            el.querySelector(".camera-input").style.display = "none";
            return takePicture(el);
          });
      }
      if (evt.target.className == "capture-button") {
        canvasData = cropper.getCanvasData();
        storage.put("settings", cropper.getData());
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
            return jIO.util.readBlobAsDataURL(blob);
          })
          .push(function (evt) {
            var base64data = evt.target.result,
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

}(rJS, RSVP, window, document, navigator, Cropper, console, FileReader, jIO, Promise));