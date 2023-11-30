/**
 * Selenium extensions for the ERP5 project
 */

/**
 * Wrap a promise to make it usable by selenium commands.
 *
 * If the promise is rejected, the command will fail with the promise rejection value.
 * If the promise is resolved, the resolved value is not used.
 *
 * The asynchronicity of do* method is as follow Selenium.prototype.doXXX
 * returns a function and this function will be called again and again until:
 *   * function returns true, which means step is successful
 *   * function returns false, which means step is not finished and function will be called again
 *   * an exception is raised, in that case the step is failed
 *   * global timeout is reached.
 * we implement the state management with similar approach as what's discussed
 * https://stackoverflow.com/questions/30564053/how-can-i-synchronously-determine-a-javascript-promises-state
 *
 * @param {Promise} promise the promise to await
 * @returns {() => boolean}
*/
function wrapPromise(promise) {
  /** @type {'pending' | 'resolved' | 'rejected'} */
  var promiseState;
  var rejectionValue;
  return () => {
    if (promiseState === 'pending') {
      return false;
    }
    if (promiseState === 'resolved') {
      return true;
    }
    if (promiseState === 'rejected') {
      Assert.fail("" + rejectionValue);
      return true
    }

    promise.then(
      function () {
        promiseState = 'resolved';
      }).catch(
        function (error) {
          console.error(error);
          promiseState = 'rejected';
          rejectionValue = error;
        }
      );
    promiseState = 'pending';
    return false;
  }
}


/**
 * You can set file data to file input field without security error.
 *   <tr>
 *    <td>setFile</td>
 *    <td>field_my_file</td>
 *    <td>/data.jpg myfilename.jpg image/jpg</td>
 *  </tr>
 *
 * @param {string} locator the selenium locator
 * @param {string} url_filename_mimetype the URL, filename and optionally mime type,
 *  separated by spaces
 * @returns {() => boolean}
 */
Selenium.prototype.doSetFile = function(locator, url_filename_mimetype) {
  var tmpArray = url_filename_mimetype.split(' ', 3);
  var url = tmpArray[0];
  var fileName = tmpArray[1];
  var mimeType = tmpArray[2] || 'application/octet-stream';

  if (!fileName) {
    throw new Error('file name must not be empty.');
  }
  var fileField = this.page().findElement(locator);
  return wrapPromise(
    fetch(url)
      .then(function(response) {
        if (!response.ok) {
          throw new Error('HTTP error, status = ' + response.status);
        }
        return response.blob();
      })
      .then(function(blob) {
        var dT =
          /* Firefox < 62 workaround exploiting https://bugzilla.mozilla.org/show_bug.cgi?id=1422655 */
          new ClipboardEvent('').clipboardData ||
          /* specs compliant (as of March 2018 only Chrome) */
          new DataTransfer();
        dT.items.add(new File([blob], fileName, {type: mimeType}));
        fileField.files = dT.files;
        fileField.dispatchEvent(new Event('change', { bubbles: true }));
      }));
};


/**
 * Checks the element referenced by `locator` is a float equals to `text`.
 * Values are converted to float, to be format-independant (ie. 1 000 = 1000.0)
 */
Selenium.prototype.assertFloat = function(locator, text) {
    var actualValueText = getText(this.page().findElement(locator));
    var actualValue = parseFloat(actualValueText.replace(/ /g, "").replace(/&nbsp;/g, ""));
    var expectedValue = parseFloat(text.replace(/ /g, "").replace(/&nbsp;/g, ""));

    if (isNaN(actualValue)) {
        Assert.fail("Actual value "+ actualValueText +
                        " cannot be parsed as float");
    }
    Assert.matches(expectedValue.toString(), actualValue.toString());
};


/**
 * like assertFloat, but for the value of <input elements.
 */
Selenium.prototype.assertFloatValue = function(locator, text) {
    var actualValueText = getInputValue(this.page().findElement(locator));
    var actualValue = parseFloat(actualValueText.replace(/ /g, "").replace(/&nbsp;/g, ""));
    var expectedValue = parseFloat(text.replace(/ /g, "").replace(/&nbsp;/g, ""));

    if (isNaN(actualValue)) {
        Assert.fail("Actual value "+ actualValueText +
                        " cannot be parsed as float");
    }
    Assert.matches(expectedValue.toString(), actualValue.toString());
};


/**
 * Checks the portal status message.
 */
Selenium.prototype.assertPortalStatusMessage = function(text) {
    var psm_locator = "css=div.transition_message";
    var actualValue = getText(this.page().findElement(psm_locator));
    Assert.matches(text, actualValue);
};

/*
 * Get the location of the current page. This function is missing in
 * Selenium 0.8 or later.
 */
Selenium.prototype.getAbsoluteLocation = function() {
    return this.page().location || this.browserbot.getCurrentWindow().location;
};

Selenium.prototype.doPhantomRender = function(filename) {
    if (window.page && window.page.render) {
        page.render(filename);
    }
};

Selenium.prototype.assertElementPositionRangeTop = function(locator, range){
    var positionTop = parseFloat(this.getElementPositionTop(locator));
    /* example of range 450..455 */
    var rangeList = range.split("..");
    var minimumPositionTop = parseFloat(rangeList[0]);
    var maximumPositionTop = parseFloat(rangeList[1]);
    if (positionTop < minimumPositionTop || positionTop > maximumPositionTop ){
      Assert.fail(positionTop + " is not between " + minimumPositionTop + " and " + maximumPositionTop);
    }
};

// a memo test pathname => image counter
var imageMatchReference = new Map();
// reset this when starting a new test.
var HtmlTestRunnerControlPanel_reset = window['HtmlTestRunnerControlPanel'].prototype.reset;
window['HtmlTestRunnerControlPanel'].prototype.reset = function() {
  imageMatchReference.clear();
  return HtmlTestRunnerControlPanel_reset.call(this);
}

function getReferenceImageCounter(testPathName) {
  var counter = imageMatchReference.get(testPathName) || 0;
  counter = counter + 1;
  imageMatchReference.set(testPathName, counter);
  return counter;
}

function getReferenceImageURL(testPathName) {
  var imageCounter = getReferenceImageCounter(testPathName);
  return testPathName + '-reference-snapshot-' + imageCounter + '.png';
}

/**
 *
 * Helper function to generate a DOM elements
 *
 * @param {string} tagName name of the element
 * @param {Node[]} [childList] list of child elements
 * @param {Object} [attributeDict] attributes
 * @param {string} [textContent]
 * @return {HTMLElement}
 */
function generateElement(tagName, childList, attributeDict, textContent) {
  var element = document.createElement(tagName);
  if (attributeDict) {
    for (var attr in attributeDict) {
      element.setAttribute(attr, attributeDict[attr]);
    }
  }
  if (childList) {
    childList.map(child => {
      element.appendChild(child);
    });
  }
  if (textContent) {
    element.textContent = textContent;
  }
  return element;
}

/**
 * verify that the rendering of the element `locator` matches the previously saved reference.
 *
 * Note that this is implemented as do* method and not a assert* method because only do* methods are asynchronous.
 *
 * @param {string} locator - an element locator
 * @param {string} misMatchTolerance - the percentage of mismatch allowed. If this is 0, the
 *      images must be exactly same. If more than 0, image will also be resized.
 * @param {boolean} haltOnFailure - define the behavior on failure: stop (assert*) or continue (verify*)
 * @returns {() => boolean}
 */
Selenium.prototype.doVerifyImageMatchSnapshot = (
  locator,
  misMatchTolerance,
  haltOnFailure
) => {
  if (window['ignoreSnapshotTest'].checked){
    // calling getReferenceImageCounter has the side effect
    // of increasing the counter, so if we enable / disable
    // snapshot mid test the counter stays in sync.
    var snapshotCounter = getReferenceImageCounter(
      testFrame.getCurrentTestCase().pathname);
    console.log("ignoring snapshot test " + snapshotCounter);
    return;
  }

  var misMatchToleranceFloat = parseFloat(misMatchTolerance);
  if (isNaN(misMatchToleranceFloat)) {
    misMatchToleranceFloat = 0;
  }

  /** @type {Promise<HTMLCanvasElement>} */
  var canvasPromise;

  /** @type {HTMLElement} */
  var element = selenium.browserbot.findElement(locator);

  if (element.nodeName == 'CANVAS' /* instanceof HTMLCanvasElement XXX ? */) {
    canvasPromise = Promise.resolve(element);
  } else {
    // create a canvas in the same document, so that if this document has loaded
    // extra fonts they are also available.
    // As suggested on https://github.com/niklasvh/html2canvas/issues/1772
    var destinationCanvas = element.ownerDocument.createElement("canvas");
    destinationCanvas.width = element.scrollWidth;
    destinationCanvas.height = element.scrollHeight;
    canvasPromise = html2canvas(element, { canvas: destinationCanvas });
  }

  return wrapPromise(
    canvasPromise
      .then(canvas => {
        return canvas.toDataURL();
      })
      .then(actual => {
        var referenceImageURL = getReferenceImageURL(
          testFrame.getCurrentTestCase().pathname
        );
        return fetch(referenceImageURL)
          .then(response => {
            if (response.status === 200) {
              return response.blob();
            }
            throw new Error('Fetching reference failed ' + response.statusText);
          })
          .then(
            blob => {
              return new Promise((resolve, reject) => {
                var fr = new FileReader();
                fr.onload = () => resolve(fr.result);
                fr.onerror = reject;
                fr.readAsDataURL(blob);
              });
            },
            () => {
              // fetching reference was not found, return empty image instead, it will be different
              // (unless the tolerance is too high)
              return document.createElement('canvas').toDataURL();
            }
          )
          .then(expected => {
            return new Promise(resolve => {
              var comparator = resemble(actual)
                .outputSettings({
                  useCrossOrigin: false
                })
                .compareTo(expected);
              if (misMatchToleranceFloat > 0) {
                comparator = comparator.scaleToSameSize();
              }
              comparator.onComplete(resolve);
            });
          })
          .then(diff => {
            if (diff.rawMisMatchPercentage > misMatchToleranceFloat) {
              htmlTestRunner.currentTest.currentRow.trElement
                .querySelector('td')
                .appendChild(
                  generateElement('div', [
                    generateElement('b',
                      [document.createTextNode('Images are ' + diff.misMatchPercentage + '% different.')]
                    ),
                    generateElement('br'),
                    document.createTextNode('Image differences:'),
                    generateElement('br'),
                    generateElement('img', [], {
                      src: diff.getImageDataUrl(),
                      alt: 'Image differences'
                    }),
                    generateElement('br'),
                    document.createTextNode('Size differences: ' + JSON.stringify(diff.dimensionDifference)),
                    generateElement('br'),
                    document.createTextNode('Click '),
                    generateElement('a', [document.createTextNode('here')], {
                      href: actual,
                      download: referenceImageURL.split('/').pop(),
                    }),
                    document.createTextNode(' to download actual image for '),
                    generateElement('code', [
                      generateElement('a', [
                        document.createTextNode(referenceImageURL),
                      ],
                        { href: referenceImageURL + '/manage_main' }
                      )
                    ])
                  ])
                );
              htmlTestRunner.currentTest.result.failed = true;
              htmlTestRunner.currentTest.result.failureMessage = 'Snapshots do not match';
              if (haltOnFailure) {
                throw new Error('Snapshots do not match');
              }
            }
          });
      }));
};

/**
 * Assert that the rendering of the element `locator` matches the previously saved reference.
 */
Selenium.prototype.doAssertImageMatchSnapshot = (
  locator,
  misMatchTolerance,
) => {
  return Selenium.prototype.doVerifyImageMatchSnapshot.bind(this)(locator, misMatchTolerance, true);
}

/**
 * Wait for fonts to be loaded.
 *
 * This is useful before checking snapshot
 */
Selenium.prototype.doWaitForFontsLoaded = function() {
  return wrapPromise(this.page().getDocument().fonts.ready);
}