# -*- coding: utf-8 -*-
"""
Extension to find receipts inside images.
Most of the functions is code from ocropy binaries modified
to work inside erp5 and adapt to receipt binaries and with more
explanation
https://github.com/tmbdev/ocropy
"""
# pylint: disable=unpacking-non-sequence
# Pylint is confused by ocropy.

import numpy as np
import scipy.ndimage as ndi
from six.moves import cStringIO as StringIO
from matplotlib import pylab
import matplotlib.image as mpimg
import scipy.stats as stats
import re
import cPickle
import ocrolib

def getReceiptValue(self, image_data, model_name = "en-default.pyrnn"):
  """
  Function called from an erp5 script through externalMethod
  that take an image and its name and save its binarized
  version in the image portal.
  ----------------------------
    @args:
      - self: object
          Represent the erp5 object from which externalmethods or module
          objects can be called
      - image_data:
          Representation of the image to analyse
    @return:
      - anon: float
          Represent total value paid on the receipt
  ----------------------------
  This function look for euros only and return a price with a two digit
  precison like "135.79" or "43,89".
  """
  image_as_string = StringIO(image_data)
  image_as_array = mpimg.imread(image_as_string, format = 'JPG')
  line_list, cleared = getLinesFromPicture(image_as_array)

  # Start the neural network
  network, lnorm = initRnnModel(model_name)
  return findReceiptValue(line_list, cleared, network, lnorm)

def findReceiptValue(line_list, cleared, network, lnorm):
  """
  Function that run the neural network through the receipt and extract
  meaningfull value
  -----------------------------
    @args:
      - lines: array list
          Represent lines of text that will be extracted
          from the image
      - cleared:2D array
          Represent binarized image cropped and cleaned,
          from which we will extract text lines
      - network: lstm object
          Represent the trained neural net
      - lnorm: method from lstm object
          Represent the size of the lstm object. Is used to scale the objects
          to recognize from original size to the average network object.
    @return:
      - anon: float
          Represent total value paid on the receipt
  -----------------------------
  This function can bemodified to add more field to detect. It might be
  possible to run a classification neural net on the result.
  """
  value_list = []
  tofind = r"(EUR)|€|(TOT)"
  for _, line in enumerate(line_list):
    binline = ocrolib.extract_masked(1 - cleared, line, 3, 3)
    # Corner case: he dewarping function from the normalizer fail
    # sometimes on empty lines. Can be corrected with better segmentation
    try:
      evaluate  = getStringFromImage(binline, lnorm, network)
      if re.search(tofind, evaluate.upper()):
        number = re.findall(r"\d+[\.|,]\d\d", evaluate)
        value_list += [float(char.replace(',', '.')) for char in number]
    except ValueError:
      pass
  return round(max(value_list), 2)

def getRnnModelFromDataStream(self, model_name="en-default.pyrnn"):
  """
  This function load a neural network from a dataStream
  ----------------------------
    @args:
      - model_name: string, default: en-default.pyrnn
          Id of the object in data_stream_module that contain the rnn model
    @return:
      - network: lstm object
          Represent the trained neural net
      - lnorm: method from lstm object
          Represent the size of the lstm object. Is used to scale the objects
          to recognize from original size to the average network object.
  ----------------------------
  WARNING: This function present a security issue and should NOT be called with
  an user-defined model name (see cpickle security issue)
  """
  network = cPickle.loads(self.data_stream_module[model_name].getData())
  lnorm = getattr(network, "lnorm", None)
  return network, lnorm

def initRnnModel(model_name = "en-default.pyrnn"):
  """
  This function load the neural network model from slapos backend
  and initialise it.
  ----------------------------
    @args:
      - model_name: string, default: en-default.pyrnn
          Id of the object in the filesystem that contain the rnn model
    @return:
      - network: lstm object
          Represent the trained neural net
      - lnorm: method from lstm object
          Represent the size of the lstm object. Is used to scale the objects
          to recognize from original size to the average network object.
  ----------------------------
  LSTM meaning: https://en.wikipedia.org/wiki/Long_short-term_memory
  lnorm is extracted for clarity. This function initialize the neural net after
  loading.
  """
  network = ocrolib.load_object(model_name)
  for node in network.walk():
    if isinstance(node, ocrolib.lstm.LSTM):
      node.allocate(5000)
  lnorm = getattr(network, "lnorm", None)

  return network, lnorm

def getLinesFromPicture(image_as_array):
  """
  Function that take an colorized image in argument and return a
  cleared binarized image and a list of lines
  ----------------------------
    @args:
      - image_as_array: 3d array
          Represent a colored image
    @return:
      - lines: array list
          Represent lines of text that will be extracted
          from the image
      - cleared:2D array
          Represent binarized image cropped and cleaned,
          from which we will extract text lines
  ----------------------------
  This function find the text position of text line in an image
  The neural network recognition only works on independant lines
  of a binarized image.
  Could be improved by making this function return each line as
  independant picture
  """
  grey_image = convertGreyscale(image_as_array)
  cropped_image = cropImage(grey_image)
  binarized_image = imageBinarization(cropped_image)
  binary = 1 - binarized_image
  cleaned, scale = removeObjects(binary)
  angle = getEstimatedSkewAngle(cleaned, np.linspace(-4, 4, 24))
  cleaned = ndi.interpolation.rotate(
    cleaned, angle, mode='constant', reshape = 0
  )
  segmentation = getSegmentizedImage(cleaned, scale)
  # Sort the labels from top to bottom
  line_list = ocrolib.compute_lines(segmentation, scale)
  order = ocrolib.reading_order([line.bounds for line in line_list])
  sorted_lines = ocrolib.topsort(order)
  # Renumber the labels with growing values
  total_labels = np.amax(segmentation) + 1
  renumber = np.zeros(total_labels, 'i')
  for i, line in enumerate(sorted_lines):
    renumber[line_list[line].label] = 0x010000 + (i + 1)
  segmentation = renumber[segmentation]
  line_list = [line_list[i] for i in sorted_lines]
  return line_list, cleaned


def getStringFromImage(image, lnorm, network):
  """
  Function that use a neural network to get a string of character from
  an image that contain a line of text
  ------------------------------------
    @args:
      - image: 2D array
          Represent a binarized image that contain a line of text
      - lnorm: norm attribute of the neural network
          Used to scale the letters from the image to the text of the
          neural network
      - network: neural network
          Used to predict text
    @return:
      - pred: string
          Text extracted from image
  ------------------------------------
  Getting the text of each line allow the neural network not to be confused
  with noise.
  """
  temp = np.amax(image) - image
  temp = temp * 1.0 / np.amax(temp)
  lnorm.measure(temp)
  image = lnorm.normalize(image, cval = np.amax(image))
  image = ocrolib.lstm.prepare_line(image, 16)
  return network.predictString(image)

def getLineSeed(binary, scale, bottom, top):
  """
  Function that find "line seeds" inside a binarized image. The line
  seeds are multiple boxes that surround text in a picture.
  --------------------------------------
    @args:
      - binary: 2D array
            Represent the image from which line seed will be extracted
      - scale: double
            Represent the size of the average object
      - bottom: 2D array
            Represent the bottom boundary of line seeds
      - top: 2D array
            Represent the top boundary of line seeds
  --------------------------------------
  The line seeds act as a "mask" that isolate lines from each other
  to allow segmentation
  """
  # Use scale as a int
  vrange = int(scale)
  threshold = 0.1
  # Find the bottom boundary
  bmarked = ndi.maximum_filter(
    bottom == ndi.maximum_filter(bottom, (vrange, 0)), (2, 2))
  bmarked = bmarked*(bottom > threshold * np.amax(bottom) * threshold)
  # Find the top boundary
  tmarked = ndi.maximum_filter(
    top == ndi.maximum_filter(top,(vrange, 0)), (2, 2))
  tmarked = tmarked * (top > threshold * np.amax(top) * threshold / 2)
  tmarked = ndi.maximum_filter(tmarked, (1, 20))
  # Create seeds
  seeds = np.zeros(binary.shape, 'i')
  line_spacing = vrange / 2
  for x in range(bmarked.shape[1]):
    transitions = sorted([(y, 1) for y in pylab.find(bmarked[ : , x])] \
                         + [(y, 0) for y in pylab.find(tmarked[ : , x])])[:: -1]
    transitions += [(0, 0)]
    for i in range(len(transitions) - 1):
      y0, s0 = transitions[i]
      if s0 == 0:
        continue
      seeds[y0 - line_spacing : y0, x] = 1
      y1, s1 = transitions[i + 1]
      if s1 == 0 and (y0 - y1) < 5 * scale:
        seeds[y1 : y0, x] = 1
  return ndi.maximum_filter(seeds, (1, vrange))

def getSegmentizedImage(binary, scale):
  """
  Function that give every pixel of every text character on a same line
  the same value so it can be easily separated latter
  This function find the upper and lower boundaries of text lines with
  a filter using the first derivative of gaussian kernel to get
  horizontal change of intensity and stretching it
  ----------------------------
    @args:
      binary: 2D array
          Represent a clean, straight binarized image from witch we will
          find the seeds
      scale: double
          Represent the size of the mean object
    @return:
      segmentation: 2D array
          Represent a picture with different pixel value for each line
          of text.
  ----------------------------
  The segmentization give us independant text lines. Rotating the
  picture to make lines more straight could improve result.
  Some args could be added to play on the stretching of the blur or
  the threeshold for finding the mask boundaries
  """
  boxmap = ocrolib.compute_boxmap(binary, scale, threshold = (.25, 4))
  cleaned_image = boxmap * binary
  # Finding horizontals gradient
  gradient = ndi.gaussian_filter(1.0 * cleaned_image, (0.5 * scale,
                                    scale * 6), order = (1, 0))
  gradient = ndi.uniform_filter(gradient,(1, 20))
  # Find the bottom (whiter) and top (darker) zones from grad
  bottom = ocrolib.norm_max((gradient < 0) * (-gradient))
  top = ocrolib.norm_max((gradient > 0) * gradient)
  seeds = getLineSeed(cleaned_image, scale, bottom, top)
  # Label the seeds then group them by line inside boxmaps
  seeds,_ = ocrolib.morph.label(seeds)
  labels = ocrolib.morph.propagate_labels(boxmap, seeds, conflict = 1)
  spread = ocrolib.morph.spread_labels(seeds, maxdist = (scale / 4))
  labels = np.where(labels > 0, labels, spread * binary)
  return labels * binary



def removeObjects(binarized):
  """
  This function identify objects as contigunious spot of white on a
  black image and remove the bigger  and smaller ones.
  ---------------------------
    @args:
      binarized: 2D array
          Represent the inversed color binarized picture from which
          objects bigger than the mean will be taken from.
    @return:
      binarized: 2D array
          "cleaned" array
      scale: double
          Represent the size of the mean object
  ---------------------------
  This function improve line detection and "clean" the image.

  A coefficient could be added to the function to change the value of
  height and width of the deleted object, or to choose only horizontal
  or vertical objects.
  """
  labels, n = ocrolib.morph.label(binarized)
  objects = ocrolib.morph.find_objects(labels)
  # Calculate the median of all objects
  bysize = sorted(objects, key = ocrolib.sl.area)
  scalemap = np.zeros(binarized.shape)
  for sub_object in bysize:
    if np.amax(scalemap[sub_object]) > 0:
      continue
    scalemap[sub_object] = ocrolib.sl.area(sub_object) ** 0.5
  scale = ndi.median(scalemap[(scalemap > 3) & (scalemap < 100)])
  # Take the mesurement of small objects
  sums = ndi.measurements.sum(binarized, labels, range(n + 1))
  sums = sums[labels]
  # Find all objects and remove big ones
  for i, b in enumerate(objects):
    if (ocrolib.sl.width(b) > scale * 8) \
    or (ocrolib.sl.height(b) > scale * 8):
      labels[b][labels[b] == i + 1] = 0
  # Recreate an array without big objects
  binarized = np.array(labels != 0, 'B')
  # Remove small objects from this image
  binarized = np.minimum(binarized, 1 - (sums > 0) * (sums < scale))
  return binarized, scale

def getEstimatedSkewAngle(image, angle_list):
  """
  Function that estimate at which angle the image is the most
  straight
  -------------------------------
    @args:
      - image: 2d array
          Represent the greyscale original image
      - angle_list: float list
          Represent the list of angles that will be tested in the
          function
    @return:
      a: float
          Represent the value of the angle (in degrees) for which the
          image is the less skew
  -------------------------------
  This function is needed to get a better segmentation (since the
  segmentation is done horizontally). It calculate the mean of each
  line in the picture then calculate the variance, and return the
  angle value for which the variance is the highest.
  """
  estimates = []
  for angle in angle_list:
    mean = np.mean(ndi.interpolation.rotate(
      image, angle, order = 0, mode = 'constant'), axis = 1)
    variance = np.var(mean)
    estimates.append((variance, angle))
  _, angle = max(estimates)
  return angle

def removeBackground(image, percentile=50):
  """
  Function that help flatten the image by estimating locals
  whitelevels. This remove local extremes and give an image with
  homogenous background and no details
  ------------------------------
    @args:
      - image: 2D array
            Represent a greyscale image
      - percentile: integer between -100 and 100
            A percentile filter with a value of 50 is basically a
            median filter, value of 0 is a minimum filter and with
            a value of 100 a maximum filter
    @return:
      - 2D array
            Represent a greyscale image with no local extreme
  ------------------------------
  The filter result will be substracted from the original image
  to make that only local extremes stand out.
  A Kuwahara filter might give better results.
  """
  # Reduce extreme differences in the greyscale image
  image = image - pylab.amin(image)
  image /= pylab.amax(image)
  white_image = ndi.filters.percentile_filter(image, percentile, size=(80, 2))
  white_image = ndi.filters.percentile_filter(white_image, percentile, size=(2, 80))
  # Get the difference between the whiteleveled image and the
  # original one and put them betewwn 0 an 1
  return np.clip(image - white_image + 1, 0, 1)

def cropImage(image):
  """
  Function that perform cropping and flattening -- Removing
  homogenous background and small extremes-- on an image.
  -------------------------------
    @args:
      grey: 2D array
          Represent the original greyscale image
    @return:
      flat: 2D array
          Represent the original image cropped and flattened
  -------------------------------
  This function reduce the size of the image and clear noise from
  homogenous background
  """
  # Reduce extreme differences in the greyscale image
  white_image = removeBackground(image)

  # Calculate coordinate to crop the image, can be done in another
  # function to improve readability
  mask = ndi.gaussian_filter(
    white_image, 7.0) < 0.9 * np.amax(white_image)
  coords = np.argwhere(mask)
  # Bounding box of kept pixels.
  x_min, y_min = coords.min(axis = 0)
  x_max, y_max = coords.max(axis = 0)
  return white_image[x_min - 10 : x_max + 10, y_min - 10 : y_max + 10]


def imageBinarization(flattened_image):
  """
  Fontion that take a flattened image and binarize it to make OCR
  easier
  -------------------------------
    @args:
      - flattened_image: 2D array
            Represent a greyscale image
    @return:
      - binarized_image: 2D array
            Represent a binarized image
  -------------------------------
  Binarized image is needed to get text boundaries and make text
  easier to distinguish from background.
  """
  gaussian_image = ndi.gaussian_filter(flattened_image, 1)
  # Applying a Gaussian filter with a small sigma and substracting
  # it from the "original" image allow to do an approximation of
  # Laplacian.
  blurred_gaussian = ndi.gaussian_filter(gaussian_image, 3)
  # Add the scaled Laplacian to the smoothed image to sharpen its edges
  sharpened = 1.5 * gaussian_image - blurred_gaussian
  # Estimate low and high threshold
  low = stats.scoreatpercentile(sharpened.ravel(), 5)
  high = stats.scoreatpercentile(sharpened.ravel(), 70)
  # rescale the image to enhance differences
  sharpened = (sharpened - low) / (high - low)
  sharpened = np.clip(sharpened, 0, 1)
  # Binarization
  return sharpened > 0.7


def convertGreyscale(image):
  """
  Function that take a three dimension numpy array
  representing a RGB picture and return a two dimension
  numpy array of this picture in greyscale with values between
  0 and 1
    @args:
      - image: 3 dimension numpy array from a RGB picture with
          values between 0 and 255
    @return:
      grey: 2 dimension numpy array with values between 0 and 1

 The greyscale conversion is needed to detect edge in
 the preprocessing and later to extract easier to process data
  """
  return image.astype(float).sum(axis = -1) / 3. / 255
