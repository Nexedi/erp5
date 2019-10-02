/**
 * Selenium extensions for the ERP5 project
 */

/**
 * You can set file data to file input field without security error.
 *   <tr>
 *    <td>setFile</td>
 *    <td>field_my_file</td>
 *    <td>/data.jpg myfilename.jpg</td>
 *  </tr>
 */
Selenium.prototype.doSetFile = function(locator, url_and_filename) {
  var tmpArray = url_and_filename.split(' ', 2);
  var url = tmpArray[0];
  var fileName = tmpArray[1];
  var rejectionValue,
    promiseState;
  // same technique as doVerifyImageMatchSnapshot below
  var assertFileSet = () => {
    if (promiseState === 'pending') {
      return false;
    }
    if (promiseState === 'resolved') {
      return true;
    }
    if (promiseState === 'rejected') {
      Assert.fail(rejectionValue);
    }
    promiseState = 'pending';

    if (!fileName) {
      throw new Error('file name must not be empty.');
    }
    var fileField = this.page().findElement(locator);
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
        dT.items.add(new File([blob], fileName));
        fileField.files = dT.files;
      })
      .then(
        function() {
          promiseState = 'resolved';
        },
        function(error) {
          console.error(error);
          promiseState = 'rejected';
          rejectionValue = 'Error setting file ' + error;
        }
      );
  }
  return assertFileSet;
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
    var psm_locator = "//div[@id='transition_message']";
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
// TODO: reset this on testSuite.reset(), because we cannot re-run a test.
imageMatchReference = new Map();

function getReferenceImageCounter(testPathName) {
  var counter = imageMatchReference.get(testPathName);
  if (counter !== undefined) {
    return counter;
  }
  counter = imageMatchReference.size + 1;
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
 * @param {Node?} childList list of child elements
 * @param {Map<string,any>?} attributeDict attributes
 * @param {string?} textContent
 * @return {Node}
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
  return element;
}

/**
 * Generate an HTML form to update the reference snapshot
 *
 * @param {string} referenceImageURL relative URL of the reference image
 * @param {string} newImageData the new image data, base64 encoded
 * @param {Map<string,any>?} attributeDict attributes
 * @return {Promise<string>} the base64 encoded html form
 */
function generateUpdateForm(referenceImageURL, newImageData) {
  return new Promise((resolve, reject) => {
    var fr = new FileReader();
    fr.onerror = reject;
    fr.onload = () => resolve(fr.result);
    fr.readAsDataURL(
      new Blob(
        [
          generateElement('html', [
            generateElement('body', [
              generateElement('p', [
                document.createTextNode('Replacing this old snapshot:'),
                generateElement('br'),
                generateElement('img', [], {
                  src: location.origin + referenceImageURL,
                  alt: 'reference image'
                }),
                generateElement('br'),
                document.createTextNode('with this new snapshot:'),
                generateElement('br'),
                generateElement('img', [], {
                  src: newImageData,
                  alt: 'new image'
                })
              ]),
              generateElement(
                'form',
                [
                  generateElement('input', [], {
                    type: 'hidden',
                    name: 'image_data',
                    value: newImageData
                  }),
                  generateElement('input', [], {
                    type: 'hidden',
                    name: 'image_path',
                    value: referenceImageURL
                  }),
                  generateElement('input', [], {
                    type: 'submit',
                    value: 'Update Reference Snapshot'
                  })
                ],
                {
                  action:
                    location.origin +
                    '/' +
                    referenceImageURL.split('/')[1] + // ERP5 portal
                    '/Zuite_updateReferenceImage',
                  method: 'POST'
                }
              )
            ])
          ]).innerHTML
        ],
        { type: 'text/html' }
      )
    );
  });
}

/**
 * verify that the rendering of the element `locator` matches the previously saved reference.
 *
 * Arguments:
 *   locator - an element locator
 *   misMatchTolerance - the percentage of mismatch allowed. If this is 0, the
 *      images must be exactly same. If more than 0, image will also be resized.
 */
Selenium.prototype.doVerifyImageMatchSnapshot = (
  locator,
  misMatchTolerance
) => {
  // XXX this is a do* method and not a assert* method because only do* methods are
  // asynchronous.
  // The asynchronicity of do* method is as follow Selenium.prototype.doXXX
  // returns a function and this function will be called again and again until:
  //   * function returns true, which means step is successfull
  //   * function returns false, which means step is not finished and function will be called again
  //   * an execption is raised, in that case the step is failed
  //   * global timeout is reached.
  // we implement the state management with similar approach as what's discussed
  // https://stackoverflow.com/questions/30564053/how-can-i-synchronously-determine-a-javascript-promises-state
  var promiseState, rejectionValue, canvasPromise;
  return function assertCanvasImage() {
    if (promiseState === 'pending') {
      return false;
    }
    if (promiseState === 'resolved') {
      return true;
    }
    if (promiseState === 'rejected') {
      Assert.fail(rejectionValue);
    }

    misMatchTolerance = parseFloat(misMatchTolerance);
    if (isNaN(misMatchTolerance)) {
      misMatchTolerance = 0;
    }
    promiseState = 'pending';
    element = selenium.browserbot.findElement(locator);
    if (element.nodeName == 'CANVAS' /* instanceof HTMLCanvasElement XXX ? */) {
      canvasPromise = Promise.resolve(element);
    } else {
      canvasPromise = html2canvas(element);
    }

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
            throw new Error('Feching reference failed ' + response.statusText);
          })
          .then(
            blob => {
              return new Promise((resolve, reject) => {
                var fr = new FileReader();
                fr.onload = d => resolve(fr.result);
                fr.onerror = reject;
                fr.readAsDataURL(blob);
              });
            },
            e => {
              // fetching reference was not found, return empty image instead, it will be different
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
              if (misMatchTolerance > 0) {
                comparator = comparator.scaleToSameSize();
              }
              comparator.onComplete(resolve);
            });
          })
          .then(diff => {
            if (diff.rawMisMatchPercentage <= misMatchTolerance) {
              promiseState = 'resolved';
            } else {
              return generateUpdateForm(referenceImageURL, actual).then(
                updateReferenceImageForm => {
                  htmlTestRunner.currentTest.currentRow.trElement
                    .querySelector('td')
                    .appendChild(
                      generateElement('div', [
                        document.createTextNode('Image differences:'),
                        generateElement('br'),
                        generateElement('img', [], {
                          src: diff.getImageDataUrl(),
                          alt: 'Image differences'
                        }),
                        generateElement('br'),
                        document.createTextNode('Click '),
                        generateElement(
                          'a',
                          [document.createTextNode('here')],
                          {
                            href: updateReferenceImageForm
                          }
                        ),
                        document.createTextNode(
                          ' to update reference snapshot.'
                        )
                      ])
                    );

                  promiseState = 'rejected';
                  rejectionValue =
                    'Images are ' + diff.misMatchPercentage + '% different';
                }
              );
            }
          });
      })
      .catch(error => {
        console.error(error);
        promiseState = 'rejected';
        rejectionValue = 'Error computing image differences ' + error;
      });
  };
};
