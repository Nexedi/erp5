# -*- coding: utf-8 -*-
"""
Extension to extract text from documents
"""
# pylint: disable=unpacking-non-sequence
# Pylint is confused by ocropy.

import numpy as np
import scipy.ndimage as ndi
from matplotlib import pylab
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
  grey_image = self.DocumentCleaning_convertToGreyscale(image_data)
  cleared_image = self.DocumentCleaning_removeBackground(grey_image)
  cropped_image = self.DocumentCleaning_cropImage(cleared_image)
  sharpened_image = self.DocumentCleaning_sharpenImage(cropped_image)
  binarized_image = self.DocumentCleaning_binarizeImage(sharpened_image)
  binary = 1 - binarized_image
  cleaned, scale = self.DocumentCleaning_removeObjects(binary)
  angle = self.DocumentCleaning_getEstimatedSkewAngle(cleaned, np.linspace(-4, 4, 24))
  cleaned = ndi.interpolation.rotate(
    cleaned, angle, mode='constant', reshape = 0
  )
  segmentation = getSegmentizedImage(cleaned, scale)
  line_list = getLinesFromPicture(segmentation, scale)

  # Start the neural network
  network, lnorm = initRnnModel(model_name)
  return findReceiptValue(line_list, cleaned, network, lnorm)

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
  string_list = ""
  for _, line in enumerate(line_list):
    binline = ocrolib.extract_masked(1 - cleared, line, 3, 3)
    # Corner case: he dewarping function from the normalizer fail
    # sometimes on empty lines. Can be corrected with better segmentation
    try:
      string_list += getStringFromImage(binline, lnorm, network) + "\n"
    except ValueError:
      pass
  return string_list

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

def getLinesFromPicture(segmentation, scale):
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
  return line_list


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