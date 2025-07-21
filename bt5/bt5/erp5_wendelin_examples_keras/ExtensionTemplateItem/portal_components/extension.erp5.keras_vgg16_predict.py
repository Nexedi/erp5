from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions # pylint:disable=import-error
from keras.preprocessing import image # pylint:disable=import-error
import numpy as np
from io import BytesIO
import PIL.Image

model = VGG16(weights='imagenet')

def predict(image_document):
  img = PIL.Image.open(BytesIO(bytes(image_document.getData())))
  img = img.resize((224, 224))
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  preds = model.predict(preprocess_input(x))
  results = decode_predictions(preds, top=5)[0]
  return results
