# -*- coding: utf-8 -*-
"""
Extension to find receipts inside images.
Most of the functions is code from ocropy binaries modified
to work inside erp5 and adapt to receipt binaries and with more
explanation
https://github.com/tmbdev/ocropy
"""

import numpy as np
import scipy.ndimage as ndi
import StringIO
import matplotlib.pylab as pylab
import matplotlib.image as mpimg
import scipy.stats as stats
import sklearn.preprocessing as preprocess
import re
import ocrolib

def find_receipt_value(self, image_data):
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
          base64 representation of the image to analyse
    @return:
      - ret: float
          Represent total value paid on the receipt
  ----------------------------
  This function return the total value of the receipt in euros.
  """
  image_str = StringIO.StringIO(image_data)
  image_as_array = mpimg.imread(image_str, format='JPG')
  lines, cleared = get_lines_from_picture(image_as_array)

  # Start the neural network
  network, lnorm = init_rnn_model()

  ret = []
  tofind = r"(EUR)|€|(TOT)"
  for _, l in enumerate(lines):
    binline = ocrolib.extract_masked(1 - cleared, l, 3, 3)
    # Corner case: he dewarping function from the normalizer fail
    # sometimes on empty lines. Can be corrected with better segmentation
    try:
      evaluate = get_str_from_image(binline, lnorm, network)
      if re.search(tofind, evaluate.upper()):
        lst = re.findall(r"\d+[\.|,]\d\d", evaluate)
        ret += [float(s.replace(',', '.')) for s in lst]
    except:
      pass

  return round(max(ret), 2)


def init_rnn_model(model_name="en-default.pyrnn"):
  """
  This function load the neural network model from slapos backend
  and initialise it.
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
  LSTM meaning: https://en.wikipedia.org/wiki/Long_short-term_memory
  lnorm is extracted for clarity. This function initialize the neural net after
  loading.
  """
  network = ocrolib.load_object(model_name)
  for x in network.walk():
    x.postLoad()
  for x in network.walk():
    if isinstance(x, ocrolib.lstm.LSTM):
      x.allocate(5000)
  lnorm = getattr(network, "lnorm", None)

  return network, lnorm

def get_lines_from_picture(image_as_array):
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
  grey_image = convert_greyscale(image_as_array)
  flattened_image = image_transformation(grey_image)
  binarized_image = image_binarization(flattened_image)
  binary = 1 - binarized_image
  cleared = ocrolib.remove_noise(binary, 16)
  scale = ocrolib.estimate_scale(cleared)
  cleaned = delete_h_lines(cleared, scale)
  angle = estimate_skew_angle(cleaned, np.linspace(-4, 4, 24))
  cleaned = ndi.interpolation.rotate(
    cleaned, angle, mode='constant', reshape=0
  )
  segmentation = image_segmentize(cleaned, scale)
  # Sort the labels
  lines = ocrolib.compute_lines(segmentation,scale)
  order = ocrolib.reading_order([l.bounds for l in lines])
  lsort = ocrolib.topsort(order)
  # Renumber the labels
  nlabels = np.amax(segmentation)+1
  renumber = np.zeros(nlabels,'i')
  for i,v in enumerate(lsort):
    renumber[lines[v].label] = 0x010000+(i+1)
  segmentation = renumber[segmentation]
  lines = [lines[i] for i in lsort]
  return lines, cleaned


def get_str_from_image(image, lnorm, network):
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
  image = lnorm.normalize(image, cval=np.amax(image))
  image = ocrolib.lstm.prepare_line(image, 16)
  pred = network.predictString(image)
  return pred

def find_line_seed(binary, scale, bottom, top):
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
  bmarked = bmarked*(bottom>threshold * np.amax(bottom) * threshold)
  # Find the top boundary
  tmarked = ndi.maximum_filter(
    top == ndi.maximum_filter(top,(vrange,0)), (2, 2))
  tmarked = tmarked*(top>threshold * np.amax(top) * threshold / 2)
  tmarked = ndi.maximum_filter(tmarked, (1, 20))
  # Create seeds
  seeds = np.zeros(binary.shape,'i')
  delta = vrange / 2
  for x in range(bmarked.shape[1]):
    transitions = sorted([(y,1) for y in pylab.find(bmarked[:,x])] \
                         + [(y,0) for y in pylab.find(tmarked[:,x])])[::-1]
    transitions += [(0,0)]
    for l in range(len(transitions)-1):
      y0,s0 = transitions[l]
      if s0==0:
        continue
      seeds[y0-delta:y0,x] = 1
      y1,s1 = transitions[l+1]
      if s1==0 and (y0-y1)<5 * scale:
        seeds[y1:y0,x] = 1
  seeds = ndi.maximum_filter(seeds,(1,int(1+scale)))
  return seeds

def image_segmentize(binary, scale):
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
  boxmap = ocrolib.compute_boxmap(binary, scale)
  cleaned_image = boxmap*binary
  # Finding horizontals gradient
  grad = ndi.gaussian_filter(1.0 * cleaned_image, (0.5 * scale,
                                    scale * 6), order=(1,0))
  grad = ndi.uniform_filter(grad,(1, 20))
  # Find the bottom (whiter) and top (darker) zones from grad
  bottom = ocrolib.norm_max((grad < 0) * (-grad))
  top = ocrolib.norm_max((grad > 0) * grad)
  seeds = find_line_seed(cleaned_image, scale, bottom, top)
  # Label the seeds then group them by line inside boxmaps
  seeds,_ = ocrolib.morph.label(seeds)
  llabels = ocrolib.morph.propagate_labels(boxmap, seeds, conflict=1)
  spread = ocrolib.morph.spread_labels(seeds, maxdist=(scale / 4))
  llabels = np.where(llabels>0, llabels, spread*binary)
  segmentation = llabels * binary
  return segmentation


def delete_h_lines(binarized, scale):
  """
  Function that delete huge horizontal line and objects bigger than
  the average character.
  This function identify objects as contigunious spot of white on a
  black image and delete the bigger ones.
  ---------------------------
    @args:
      binarized: 2D array
          Represent the inversed color binarized picture from which
          objects bigger than the mean will be taken from.
      scale: double
          Represent the size of the mean object
    @return:
      binarized: 2D array
          "cleaned" array
  ---------------------------
  This function improve line detection and "clean" the image.
  A coefficient could be added to the function to change the value of
  height and width of the deleted object, or to choose only horizontal
  or vertical objects.
  """
  labels, _ = ocrolib.morph.label(binarized)
  objects = ocrolib.morph.find_objects(labels)
  for i,b in enumerate(objects):
    if (ocrolib.sl.width(b) > scale * 8) \
    or (ocrolib.sl.height(b) > scale * 8):
      labels[b][labels[b]==i+1] = 0
  binarized = np.array(labels!=0,'B')
  return binarized

def image_whitelevel(image):
  """
  Function that help flatten the image by estimating locals
  whitelevels. This remove local extremes and give an image with
  homogenous background and no details
  ------------------------------
    @args:
      - image: 2D array
            Represent a greyscale image
    @return:
      - m: 2D array
            Represent a greyscale image with no local extreme
  ------------------------------
  This function result will be substracted from the original image
  to make that only local extremes stand out.
  """
  m = ndi.interpolation.zoom(image, 1.)
  m = ndi.filters.percentile_filter(m, 50,size=(80, 2))
  m = ndi.filters.percentile_filter(m, 50,size=(2, 80))
  #m = ndi.interpolation.zoom(m, 1 / 1.)
  return m

def estimate_skew_angle(image, angles):
  """
  Function that estimate at which angle the image is the most
  straight
  -------------------------------
    @args:
      - image: 2d array
          Represent the greyscale original image
      - angles: float list
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
  for a in angles:
    v = np.mean(ndi.interpolation.rotate(
      image, a, order=0, mode='constant'), axis=1)
    v = np.var(v)
    estimates.append((v, a))
  _, a = max(estimates)
  return a


def image_transformation(grey):
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
  image = grey - pylab.amin(grey)
  image /= pylab.amax(image)
  white_image = image_whitelevel(image)

  # Get the difference between the whiteleveled image and the
  # original one and put them betewwn 0 an 1
  flat = np.clip(image - white_image + 1, 0, 1)
  # Calculate coordinate to crop the image, can be done in another
  # function to improve readability
  mask = ndi.gaussian_filter(
    flat, 7.0) < 0.9 * np.amax(flat)
  coords = np.argwhere(mask)
  # Bounding box of kept pixels.
  x0, y0 = coords.min(axis=0)
  x1, y1 = coords.max(axis=0)
  return flat[x0-10:x1+10, y0-10:y1+10]


def image_binarization(flattened_image):
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
  lo = stats.scoreatpercentile(sharpened.ravel(), 5)
  hi = stats.scoreatpercentile(sharpened.ravel(), 70)
  # rescale the image to enhance differences
  sharpened = (sharpened - lo) / (hi - lo)
  sharpened = np.clip(sharpened, 0, 1)
  # Binarization
  binarized_image = preprocess.binarize(sharpened, 0.7)
  return binarized_image

def convert_greyscale(image):
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
  grey = image.astype(float).sum(axis=-1) / 3.0 / 255
  return grey



########## Unused functions kept for documentation #############

def get_receipt_from_image(grey_image, threshold=175, \
                           alpha=10, sigma=2.):
  """
  Function that transform a noisy greyscale image of a receipt on
  a darker background into a smoother, sharper image of this receipt
  cropped without the mentionned background.
    @args:
      - grey_image: two dimension numpy array
          | Original greyscale image
      - threshold: integer (default 200)
          | All numpy lines and columns without a value superior
          | to this will be cropped. Should depend on the brightness
          | of the picture
      - alpha: positive integer (default 30)
          | The Laplacian filter (that overline edges) is multiplied
          | by this value to have an impact when added to the gaussian
          | filter. If its too small, it won't have an impact; if its
          | too big, it will mess with the resulting array values and
          | "replace" the gaussian filtered image.
      - sigma: positive float (default 5.)
          | The sigma is the standard derivation of the gaussian
          | filter. It quantify the dispertion of the filter. If
          | this value is too high, the picture will become too blurry.
          | If it is to low, it won't have any effect on the noise.
          | This value should be depending on image size
    @return:
      - result: two dimension numpy array
          | filtered, cropped and sharpened versin of grey_image

  This function is needed to "clean" the picture of background and
  noise without affecting the readability of the data. The gaussian
  filter could be replaced by a median filter more effective in some
  cases and the Laplacian filter by the unsharpening filter.
  See http://homepages.inf.ed.ac.uk/rbf/HIPR2/filtops.htm
  This function is unused and replaced with a set of more accurate one
  """
  # Smoothing of the image with Gaussian filter
  gaussian_image = ndi.gaussian_filter(grey_image, sigma)
  # Applying a Gaussian filter with a small sigma and substracting
  # it from the "original" image allow to do an approximation of
  # Laplacian.
  blurred_gaussian = ndi.gaussian_filter(gaussian_image, (sigma / 2))
  # Add the scaled Laplacian to the smoothed image to sharpen its edges
  sharpened = gaussian_image + alpha * (gaussian_image \
                                        - blurred_gaussian)
  # This line copy every elements greater than threshold of a
  # blurred (noiseless) array into mask and replace the others by 0
  mask = sharpened>threshold
  # Coordinates of kept pixels.
  coords = np.argwhere(mask)
  # Bounding box of kept pixels.
  x0, y0 = coords.min(axis=0)
  x1, y1 = coords.max(axis=0) + 1
  # Get the contents of the bounding box.
  result = sharpened[x0:x1, y0:y1]
  return result

def canny_edge_detection(grey_image):
  """
  See https://en.wikipedia.org/wiki/Canny_edge_detector
  Function that take a two dimension numpy array representing
  a greyscale image and return a three dimension numpy array
  showing edges of this picture.

    @args:
      - grey_image: 2 dimension numpy array
    @return
      - G: 3 dimension numpy array
          Representation of the edge gradient of the picture.

  The canny edge detection allow us to find the egdes on a picture.
  It is currently unused, kept for information/learning purpose
  """
  # A median filter is applied to reduce the image noise
  # to facilitate edge detection.
  # The median filter is supposed to be a bit better than
  # the gaussian filter for some cases, and roughly equal in other.
  # An adaptive filter can have better result it seems,
  # see the wikipedia page at label "replace gaussian filter"
  smoothed_image = np.zeros(grey_image.shape, 'double')
  ndi.median_filter(grey_image, 21, output=smoothed_image)
  # Sobel edge detection operator: first derivative in horizontal
  # direction (gx) and in vertical direction (gy)
  gx = ndi.sobel(smoothed_image, axis=0, mode='constant')
  gy = ndi.sobel(smoothed_image, axis=1, mode='constant')
  # Edge gradient G (result of the square root of gx squared
  # and gy squared)
  # You can find the direction of each edges with np.arctan2(gx, gy)
  G = np.hypot(gx, gy)
  # Non-maximum suppression aswell as double threshold are
  # not implemented/needed
  return G