from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing import image
import numpy as np
from cStringIO import StringIO
import PIL.Image

model = VGG16(weights='imagenet')

def predict(image_document):
  img = PIL.Image.open(StringIO(image_document.getData()))
  img = img.resize((224, 224))
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  preds = model.predict(preprocess_input(x))
  results = decode_predictions(preds, top=5)[0]
  return results
