# -*- coding: utf-8 -*-
"""
Extension that clean or/and improve images
"""
# pylint: disable=unpacking-non-sequence
# Pylint is confused by ocropy.

import matplotlib.image as mpimg
import StringIO
import numpy as np
import scipy.ndimage as ndi
from matplotlib import pylab
from scipy import stats
import ocrolib

def convertImageToNumpyArray(image):
  """
  Take an image and convert it into a string then
  into a numpy array
  """
  image_as_string = StringIO.StringIO(image)
  # XXX We should be able to find which format is the image
  return mpimg.imread(image_as_string, format = 'JPG')

def convertToGreyscale(image):
  """
  Function that take a three dimension numpy array
  representing a RGB picture and return a two dimension
  numpy array of this picture in greyscale with values between
  0 and 1
  --------------------------------
    @args:
      - image: 3 dimension numpy array from a RGB picture with
          values between 0 and 255
    @return:
      grey: 2 dimension numpy array with values between 0 and 1
  --------------------------------
  The greyscale conversion makes it easier multiple operations
  like Edge or text recognition.
  """
  return image.astype(float).sum(axis = -1) / 3. / 255

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
  # Calculate coordinate to crop the image, can be done in another
  # function to improve readability
  mask = ndi.gaussian_filter(
    image, 7.0) < 0.9 * np.amax(image)
  coords = np.argwhere(mask)
  # Bounding box of kept pixels.
  x_min, y_min = coords.min(axis = 0)
  x_max, y_max = coords.max(axis = 0)
  return image[x_min - 10 : x_max + 10, y_min - 10 : y_max + 10]

def sharpenImage(image):
  """
  Function that enhance angles on a picture by doing an approximation
  of laplacian after a gaussian blur
  -------------------------------
    @args:
      - image: 2D array
            Represent a greyscale image
    @return:
      - 2D array
            Represent a binarized image
  -------------------------------
  Enhacing edged help for the recognition
  """
  gaussian_image = ndi.gaussian_filter(image, 1)
  # Applying a Gaussian filter with a small sigma and substracting
  # it from the "original" image allow to do an approximation of
  # Laplacian.
  blurred_gaussian = ndi.gaussian_filter(gaussian_image, 3)
  # Add the scaled Laplacian to the smoothed image to sharpen its edges
  return 1.5 * gaussian_image - blurred_gaussian

def binarizeImage(image):
  """
  Fontion that take a flattened image and binarize it to make OCR
  easier
  -------------------------------
    @args:
      - flattened_image: 2D array
            Represent a greyscale image
    @return:
      - anon: 2D array
            Represent a binarized image
  -------------------------------
  Binarized image is needed to get text boundaries and make text
  easier to distinguish from background.
  """
  # Estimate low and high threshold
  low = stats.scoreatpercentile(image.ravel(), 5)
  high = stats.scoreatpercentile(image.ravel(), 70)
  # rescale the image to enhance differences
  sharpened = (image - low) / (high - low)
  sharpened = np.clip(sharpened, 0, 1)
  # Binarization
  return sharpened > 0.7

# XXX A function that only compute the scale could be extracted from this.
# This might not be the extension this function should be in.
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

