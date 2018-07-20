# coding: utf-8

# In[1]:


from skimage import io
from skimage.filters import threshold_sauvola
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import collections
import pytesseract
import StringIO


# In[2]:


def mean_conv(n) :
  return np.ones((n))*(1/float(n))


# In[3]:


def groupping(arr, variance) :
  # keys : group num, values : localisation
  group_loc = []
  # keys : the minimum of the group : values : group num
  min_group = {}
  groups = []
  i = 0
  current_group_num = 0
  current_group = []
  while i < len(arr) :
    group_loc.append(i)
    current_group = [arr[i]]
    groups.append(current_group_num)
    j = i+1
    while j < len(arr) :
      current_group.append(arr[j])
      if np.var(current_group) <= variance :
        groups.append(current_group_num)
        j+=1
      else :
        break
    current_group.pop()
    min_group[np.mean(current_group)] = current_group_num
    i=j
    current_group_num += 1
    current_group = []

    min_group = collections.OrderedDict(sorted(min_group.items()))
    
  return groups, min_group, group_loc

def found_border(arr, group, wich) :
  if wich == "top" or wich == "left" :
    for index, current_group in enumerate(arr) :
      if current_group == group :
        i = index+1
        while i < len(arr) :
          if arr[i] != group :
            break
          i+=1
        border = i-1
        break
  
  else :
    for index, current_group in enumerate(arr) :
      if current_group == group :
        border = index
        break
  return border


def best_group (min_group, group_loc, thresh) :
  thresh = int(thresh*len(min_group))
  i = 0
  best_group1 = min_group[min_group.keys()[0]]
  best_group2 = min_group[min_group.keys()[1]]
  
  if group_loc[best_group2] < group_loc[best_group1] :
    tmp = best_group1
    best_group1 = best_group2
    best_group2 = tmp
  
  for current_group in min_group.keys() :
    candidate = min_group[current_group]
    
    if group_loc[candidate] < group_loc[best_group1] :
      best_group1 = candidate
    elif group_loc[candidate] > group_loc[best_group2] :
      best_group2 = candidate
      
    
    i += 1
    if i >= thresh :
      break
  
  return best_group1, best_group2


# In[4]:


def crop_image(image_binary, threshold) :
  conv = mean_conv(60)
  image_binary_export = np.where(image_binary == True, 255, 0)
  
  # compute variance
  variance_col = np.var(image_binary, axis=0)
  variance_row = np.var(image_binary, axis=1)
  
  # Smoothing
  variance_col = ndi.convolve(variance_col, conv, mode='mirror')
  variance_row = ndi.convolve(variance_row, conv, mode='mirror')
  
  # Grouping
  groups_col, min_group_col, group_loc_col = groupping(variance_col, 0.00001)
  groups_row, min_group_row, group_loc_row = groupping(variance_row, 0.00001)  
  
  # Threshold 10%
  grp_col1, grp_col2 = best_group(min_group_col, group_loc_col, threshold)
  grp_row1, grp_row2 = best_group(min_group_row, group_loc_row, threshold)
  
  # Compute min
  col_start = found_border(groups_col, grp_col1, "left")
  col_end = found_border(groups_col, grp_col2, "right")
  row_start = found_border(groups_row, grp_row1, "top")
  row_end = found_border(groups_row, grp_row2, "bottom")
    
  # crop image
  image_crop = image_binary_export [row_start:row_end,col_start : col_end]
  
  
  white = image_crop.max()
  rows = np.full((10,image_crop.shape[1]), white)

  image_border = np.concatenate((rows,image_crop))
  image_border = np.concatenate((image_border, rows))

  columns = np.full((image_border.shape[0],10), white)
  image_border = np.concatenate((columns, image_border), axis=1)
  image_border = np.concatenate((image_border, columns), axis=1)
  
  return Image.fromarray(image_crop.astype("uint8"))#, Image.fromarray(image_border.astype("uint8"))


# In[6]:


def binnarize (image) :
  image = io.imread(image, as_gray=True)
  radius = int(( image.shape[0] + image.shape[1] ) * 0.03)
  if (radius % 2 == 0) :
    radius += 1

  thresh_local = threshold_sauvola(image, radius)
  image_binary = image > thresh_local
  image_binary_export = np.where(image_binary == True, 255, 0)

  return image_binary, Image.fromarray(image_binary_export.astype("uint8"))


# In[7]:


def list_crop_image(image) :
  croped_image = []
  previous_crop = False
  
  for thresh in range(50) :
    thresh /= 100.
    crop = crop_image(image, thresh)
    if crop == previous_crop :
      continue
    croped_image.append(crop)
    previous_crop = crop
    
  return croped_image


# In[8]:


def tess_prediction(image_bin) :
  result = {}
  for rotation in [0,90] :
    try :
      data = pytesseract.image_to_osd(image_bin.rotate(rotation), lang='fra+eng+jpn+chi_sim', output_type='dict')
      angle = data['orientation']
      conf = data['orientation_conf']
      result[conf] = angle+rotation

    except :
      continue
    
  if len(result) == 0 :
    conf_max = 0
    best_angle = -1
  else :
    conf_max = max(result.keys())
    best_angle = result[conf_max] % 360
    
  return best_angle, conf_max


# In[9]:


def tess_prediction_list(image_list) :
  result = {}
  for image_crop in image_list :
    angle, conf = tess_prediction(image_crop)
    try :
      if result[angle] < conf :
        result[angle] = conf
    except :
      result[angle] = conf
  return max(result, key=result.get)


# In[10]:


def orientation(image) :
  image_binnarize, image_binnarize_tesseract = binnarize(image)
  cropped_images = list_crop_image(image_binnarize)
  cropped_images.append(image_binnarize_tesseract)
  result = tess_prediction_list(cropped_images)
  
  return result

def image_well_oriented(image) :
  rotation = orientation(image)
  
  image_reoriented = Image.open(image).rotate(rotation, expand=True)
    
  # put orientation
  image_export = StringIO.StringIO()
  image_reoriented.save(image_export, 'png')
  
  return image_export
  
def rotate_image(image, rotation) :
  image_reoriented = Image.open(image).rotate(rotation, expand=True)
    
  # put orientation
  image_export = StringIO.StringIO()
  image_reoriented.save(image_export, 'png')
  
  return image_export
    